# Инициализируем Django
import os

from django import setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lesson20.settings')
setup()  # Инициализируем Django.

# Импортируем модели после инициализации.
from faker import Faker

from django.contrib.auth.hashers import make_password
from posts.models import Note, User


def create_users(limit: int):
    users: list[User] = []

    faker = Faker("ru")
    for i in range(limit):
        profile = faker.simple_profile()
        users.append(
            User(
                username=profile["username"],
                password=make_password(faker.password(length=12)),
                email=profile["mail"],
                first_name=faker.first_name(),
                last_name=faker.last_name(),
                phone=faker.phone_number()[:11],
            )
        )
    User.objects.bulk_create(users)  # Создаем сразу всех пользователей в базе


def create_notes(limit: int):
    users = User.objects.all()
    faker = Faker("ru")

    for user in users:
        notes: list[Note] = []
        for i in range(limit):
            notes.append(
                Note(
                    title=faker.sentence(nb_words=5),
                    content=faker.paragraph(nb_sentences=10),
                    user=user,
                    created_at=faker.date_between(),
                )
            )
        Note.objects.bulk_create(notes)


# Точка входа для запуска данного файла.
if __name__ == "__main__":
    # Выполняется только при непосредственном запуске этого файла.
    # create_users(100)
    create_notes(500)
