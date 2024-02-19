from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.utils import timezone
from django.http import HttpResponseRedirect, Http404, HttpRequest, HttpResponseForbidden
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import Case, When
from django.views import View

from .models import Note, User, Tag
from .service import create_note, filter_notes, queryset_optimization
from .history import HistoryPageNotes
from .email import ConfirmUserRegisterEmailSender, ConfirmUserResetPasswordEmailSender
from .forms import RegisterForm, ResetForm


def home_page_view(request: HttpRequest):
    # all_notes = Note.objects.all()
    # context: dict = {
    #     "notes": all_notes
    # }
    # return render(request, "home.html", context)
    queryset = queryset_optimization(Note.objects.all())

    # print(queryset.query)

    return render(request, "home.html", {"notes": queryset[:100]})


def filter_notes_view(request: WSGIRequest):
    """
    Фильтруем записи по запросу пользователя.
    HTTP метод - GET.
    Обрабатывает URL вида: /filter/?search=<text>
    """

    search: str = request.GET.get("search", "")  # `get` - получение по ключу. Если такого нет, то - "",

    # Если строка поиска не пустая, то фильтруем записи по ней.
    # if search:
    #     # ❗️Нет обращения к базе❗️
    #     # Через запятую запросы формируются c ❗️AND❗️
    #     # notes_queryset = Note.objects.filter(title__icontains=search, content__icontains=search)
    #     # SELECT "posts_note"."uuid", "posts_note"."title", "posts_note"."content", "posts_note"."created_at"
    #     # FROM "posts_note" WHERE (
    #     # "posts_note"."title" LIKE %search% ESCAPE '\' AND "posts_note"."content" LIKE %search% ESCAPE '\')
    #
    #     # ❗️Все импорты сверху файла❗️
    #     # from django.db.models import Q
    #
    #     # notes_queryset = Note.objects.filter(title__icontains=search, content__icontains=search)
    #     # Аналогия
    #     # notes_queryset = Note.objects.filter(Q(title__icontains=search), Q(content__icontains=search))
    #
    #     # Оператор - `|` Означает `ИЛИ`.
    #     # Оператор - `&` Означает `И`.
    #     notes_queryset = Note.objects.filter(Q(title__icontains=search) | Q(content__icontains=search))
    #
    # else:
    #     # Если нет строки поиска.
    #     notes_queryset = Note.objects.all()  # Получение всех записей из модели.
    #
    # notes_queryset = notes_queryset.order_by("-created_at")  # ❗️Нет обращения к базе❗️
    #
    # # SELECT "posts_note"."uuid", "posts_note"."title", "posts_note"."content", "posts_note"."created_at"
    # # FROM "posts_note" WHERE
    # # ("posts_note"."title" LIKE %python% ESCAPE '\' OR "posts_note"."content" LIKE %python% ESCAPE '\')
    # # ORDER BY "posts_note"."created_at" DESC
    #
    # print(notes_queryset.query)

    queryset = queryset_optimization(
        filter_notes(search)
    )

    context: dict = {
        "notes": queryset[:100],
        "search_value_form": search,
    }
    return render(request, "home.html", context)


@login_required
def create_note_view(request: WSGIRequest):
    # print(request.user)  # В каждом запросе есть пользователь!
    # НО, только если он вошел на сайте, в ином случае это аноним.

    if not request.user.is_authenticated:
        return render(request, "registration/login.html", {"errors": "Необходимо войти"})

    if request.method == "POST":
        # images: list | None = request.FILES.getlist("noteImage")
        #
        # note = Note.objects.create(
        #     title=request.POST["title"],
        #     content=request.POST["content"],
        #     user=request.user,
        #     image=images[0] if images else None,
        # )
        note = create_note(request)
        return HttpResponseRedirect(reverse('show-note', args=[note.uuid]))

    return render(request, "create_form.html")


def show_note_view(request: WSGIRequest, note_uuid):
    try:
        note = Note.objects.get(uuid=note_uuid)

    except Note.DoesNotExist:
        raise Http404

    return render(request, "note.html", {"note": note})


def show_about_us_view(request: WSGIRequest):
    return render(request, "about_us.html")


def edit_note_view(request: WSGIRequest, note_uuid):
    try:
        note = Note.objects.get(uuid=note_uuid)

    except Note.DoesNotExist:
        raise Http404

    if note.user != request.user:
        return HttpResponseForbidden("Запрещено!")

    if request.method == "POST":
        note.title = request.POST["title"]
        note.content = request.POST["content"]
        note.mod_time = timezone.now()
        if request.FILES.get("noteImage"):
            if note.image:
                note.image.delete()
            note.image = request.FILES.get("noteImage")
        note.save()
        return HttpResponseRedirect(reverse('show-note', args=[note.uuid]))

    return render(request, "edit_form.html", {"note": note})


def delete_note_view(request: WSGIRequest, note_uuid):
    note = Note.objects.get(uuid=note_uuid)
    if note.user != request.user:
        return HttpResponseForbidden("Запрещено!")
    if request.method == "POST":
        Note.objects.filter(uuid=note_uuid).delete()
    return HttpResponseRedirect(reverse("home"))


def user_posts(request: WSGIRequest, username):
    # notes = Note.objects.filter(user__username=username)
    # context: dict = {
    #     "notes": notes
    # }
    # return render(request, "home.html", context)
    queryset = queryset_optimization(
        Note.objects.filter(user__username=username)
    )
    # SELECT * FROM "posts_note"
    # INNER JOIN "users" ON ("posts_note"."user_id" = "users"."id")
    # WHERE "users"."username" = boris1992
    # ORDER BY "posts_note"."created_at" DESC

    # print(Note.objects.filter(user__username=username).query)

    return render(request, "posts-list.html", {"notes": queryset})


def user_profile(request: WSGIRequest, username):
    if request.method == "POST":
        user = User.objects.get(username=username)
        user.first_name = request.POST.get("first_name", user.first_name)
        user.last_name = request.POST.get("last_name", user.last_name)
        user.phone = request.POST.get("phone", user.phone)
        user.save()
        return HttpResponseRedirect(reverse("home"))
    all_tags = Tag.objects.filter(notes__user__username=username).distinct()

    return render(request, "profile.html", {"tags": all_tags})


def register(request: WSGIRequest):
    if request.method != "POST":
        return render(request, "registration/register.html")
    # print(request.POST)
    if not request.POST.get("username") or not request.POST.get("email") or not request.POST.get("password1"):
        return render(
            request,
            "registration/register.html",
            {"errors": "Укажите все поля!"}
        )
    # print(User.objects.filter(
    #     Q(username=request.POST["username"]) | Q(email=request.POST["email"])
    # ))
    # Если уже есть такой пользователь с username или email.
    if User.objects.filter(
            Q(username=request.POST["username"]) | Q(email=request.POST["email"])
    ).count() > 0:
        return render(
            request,
            "registration/register.html",
            {"errors": "Если уже есть такой пользователь с username или email"}
        )

    # Сравниваем два пароля!
    if request.POST.get("password1") != request.POST.get("password2"):
        return render(
            request,
            "registration/register.html",
            {"errors": "Пароли не совпадают"}
        )

    # Создадим учетную запись пользователя.
    # Пароль надо хранить в БД в шифрованном виде.
    user = User.objects.create_user(
        username=request.POST["username"],
        email=request.POST["email"],
        password=request.POST["password1"]
    )

    ConfirmUserRegisterEmailSender(request, user).send_mail()

    if user is not None:
        return HttpResponseRedirect(reverse("login"))

    return HttpResponseRedirect(reverse('home'))


def register_view(request: WSGIRequest):
    form = RegisterForm()

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password1'],
                is_active=False,
            )

            # Подтверждение по email.
            ConfirmUserRegisterEmailSender(request, user).send_mail()

            return HttpResponseRedirect(reverse("login"))

    return render(request, 'registration/register-form.html', {'form': form})


def confirm_register_view(request: WSGIRequest, uidb64: str, token: str):
    username = force_str(urlsafe_base64_decode(uidb64))

    user = get_object_or_404(User, username=username)
    if default_token_generator.check_token(user, token):
        user.is_active = True
        user.save(update_fields=["is_active"])
        return HttpResponseRedirect(reverse("login"))

    return render(request, "registration/invalid_email_confirm.html", {"username": user.username})


def reset_view(request: WSGIRequest):
    form = ResetForm()

    if request.method == 'POST':

        username = request.POST.get("username")

        form = ResetForm(request.POST)
        if form.is_valid():
            user = get_object_or_404(User, username=username)
            ConfirmUserResetPasswordEmailSender(request, user).send_mail()
            # Подтверждение по email.
            return HttpResponseRedirect(reverse("login"))

    return render(request, 'registration/reset-form.html', {'form': form})


def confirm_reset_view(request: WSGIRequest, uidb64: str, token: str):
    username = force_str(urlsafe_base64_decode(uidb64))

    user = get_object_or_404(User, username=username)
    if default_token_generator.check_token(user, token):
        new_password = request.POST.get("password1")
        user.set_password(new_password)
        user.save()
        return HttpResponseRedirect(reverse("login"))

    return render(request, "registration/invalid_email_confirm.html", {"username": user.username})


class ListHistoryOfPages(View):
    def get(self, request: WSGIRequest):
        history_service = HistoryPageNotes(request)
        uuids = history_service.history_uuids[::-1]
        ordering = Case(*(When(uuid=ident, then=pos) for pos, ident in enumerate(uuids)))
        queryset = queryset_optimization(Note.objects.filter(uuid__in=history_service.history_uuids)).order_by(ordering)
        # queryset = queryset_optimization_history(Note.objects.filter(uuid__in = history_service.history_uuids))
        return render(request, "home.html", {"notes": queryset[:100]})
