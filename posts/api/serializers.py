from django.contrib.auth import get_user_model
from rest_framework import serializers
from posts.models import Note, Tag


class ShortUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ["id", "username"]


class NoteSerializer(serializers.ModelSerializer):
    user = ShortUserSerializer(read_only=True)

    class Meta:
        model = Note
        fields = ["uuid", "title", "created_at", "image", "tags", "user"]


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name"]
