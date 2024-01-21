from django.urls import path
from .views import NoteListCreateAPIView, NoteDetailAPIView, TagListCreateAPIView

# /api/

app_name = 'posts:api'

urlpatterns = [
    # Классы представлений указываем через вызов метода `as_view`
    path("posts/", NoteListCreateAPIView.as_view(), name="notes-list-create"),
    path("posts/<id>/", NoteDetailAPIView.as_view(), name="note"),
    path("tags/", TagListCreateAPIView.as_view(), name="tags-list-create")
]
