from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseRedirect, Http404
from django.core.handlers.wsgi import WSGIRequest

from .models import Note


def home_page_view(request: WSGIRequest):
    all_notes = Note.objects.all()
    context: dict = {
        "notes": all_notes
    }
    return render(request, "home.html", context)


def create_note_view(request: WSGIRequest):
    if request.method == "POST":
        note = Note.objects.create(
            title=request.POST["title"],
            content=request.POST["content"],
        )
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
