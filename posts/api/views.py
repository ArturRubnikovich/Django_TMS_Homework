from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.pagination import PageNumberPagination
from posts.api.permissions import IsOwnerOrReadOnly
from posts.api.serializers import NoteSerializer, TagSerializer
from posts.models import Note, Tag


class NoteListCreateAPIView(ListCreateAPIView):
    """
    Класс API view, для endpoint'a просмотра перечня и создания новых заметок.
    """
    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = PageNumberPagination


class NoteDetailAPIView(RetrieveUpdateDestroyAPIView):
    """
    Класс API view, для endpoint'a просмотра, изменения и удаления одной заметки.
    """
    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    lookup_field = "uuid"  # По какому (уникальному) полю модели будет найдена заметка.
    lookup_url_kwarg = "id"  # Какой параметр указать в urlpatterns, для поиска заметки.
    permission_classes = [IsOwnerOrReadOnly]


class TagListCreateAPIView(ListCreateAPIView):
    """
    Класс API view, для endpoint'a просмотра и создания тегов.
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
