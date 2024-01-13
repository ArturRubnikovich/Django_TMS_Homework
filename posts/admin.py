from django.contrib import admin
from django.db.models import QuerySet, F
from django.db.models.functions import Upper
from django.contrib.auth.admin import UserAdmin
from django.utils.safestring import mark_safe

from .models import Note, Tag, User


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ["preview_image", "title", "created_at", "short_content", "tags_function", "user"]
    search_fields = ["title", "content"]
    date_hierarchy = "created_at"

    # Действия
    actions = ["title_up"]

    # Поля, которые не имеют большого кол-ва уникальных вариантов!
    list_filter = ["user__username", "user__email", "tags__name"]

    filter_horizontal = ["tags"]

    readonly_fields = ["preview_image"]

    fieldsets = (
        # 1
        (None, {"fields": ("title", "user", "preview_image", "image", "tags")}),
        ("Содержимое", {"fields": ("content",)})
    )

    def get_queryset(self, request):
        return (
            Note.objects.all()
            .select_related("user")  # Вытягивание связанных данных из таблицы User в один запрос
            .prefetch_related("tags")  # Вытягивание связанных данных из таблицы Tag в отдельные запросы
        )

    @admin.action(description="Upper Title")
    def title_up(self, form, queryset: QuerySet[Note]):
        queryset.update(title=Upper(F("title")))

    @admin.display(description="Содержимое")
    def short_content(self, obj: Note) -> str:
        return obj.content[:50]+"..."

    @admin.display(description="Теги")
    def tags_function(self, obj: Note) -> str:
        tags = list(obj.tags.all())
        text = ""
        for tag in tags:
            text += f"<span style=\"color: blue;\">{tag}</span><br>"
        return mark_safe(text)

    @admin.display(description="IMG")
    def preview_image(self, obj: Note) -> str:
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" height="128" />')
        return "X"


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ["name"]


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = (
        # 1  tuple(None, dict)
        (None, {"fields": ("username", "password")}),

        # 2  tuple(str, dict)
        ("Персональная информация", {"fields": ("first_name", "last_name", "email", "phone")}),

        # 3  tuple(str, dict)
        (
            "Права пользователя",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),

        # 4  tuple(str, dict)
        ("Важные даты", {"fields": ("last_login", "date_joined")}),
    )
