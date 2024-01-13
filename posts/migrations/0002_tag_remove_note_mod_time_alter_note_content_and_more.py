# Generated by Django 5.0.1 on 2024-01-13 21:59

import ckeditor_uploader.fields
import django.db.models.deletion
import posts.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='note',
            name='mod_time',
        ),
        migrations.AlterField(
            model_name='note',
            name='content',
            field=ckeditor_uploader.fields.RichTextUploadingField(verbose_name='Содержимое'),
        ),
        migrations.AlterField(
            model_name='note',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to=posts.models.upload_to, verbose_name='Превью'),
        ),
        migrations.AlterField(
            model_name='note',
            name='title',
            field=models.CharField(help_text='Укажите не более 255 символов', max_length=255, verbose_name='Заголовок'),
        ),
        migrations.AlterField(
            model_name='note',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Владелец'),
        ),
        migrations.AddField(
            model_name='note',
            name='tags',
            field=models.ManyToManyField(related_name='notes', to='posts.tag', verbose_name='Теги'),
        ),
        migrations.AddIndex(
            model_name='note',
            index=models.Index(fields=['created_at'], name='created_at_index'),
        ),
    ]
