from django.core.handlers.wsgi import WSGIRequest
from .models import Note


class HistoryPageNotes:

    def __init__(self, request: WSGIRequest):
        self._session = request.session

        self._session.setdefault("history", [])

        if not isinstance(self._session["history"], list):
            self._session["history"] = []

    def add_page(self, note: Note) -> None:
        note_uuid = str(note.uuid)
        if note_uuid in self._session["history"]:
            self._session["history"].remove(note_uuid)

        self._session["history"].append(note_uuid)
        self._session["history"] = self._session["history"][-20:]
        self._session.save()

    @property
    def history_uuids(self) -> list[str]:
        return self._session["history"]


def history_service(request: WSGIRequest) -> dict[str, list[str]]:
    return {"history_uuids": HistoryPageNotes(request).history_uuids}
