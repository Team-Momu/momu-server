# Generated by Django 3.0.8 on 2022-07-04 21:57

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Place',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('place_id', models.TextField()),
                ('place_name', models.TextField()),
                ('category_name', models.TextField()),
                ('phone', models.TextField()),
                ('road_address_name', models.TextField()),
                ('region', models.TextField()),
                ('place_x', models.TextField()),
                ('place_y', models.TextField()),
                ('place_url', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('location', models.TextField()),
                ('time', models.CharField(choices=[('brek', '아침'), ('lun', '점심'), ('din', '저녁'), ('night', '밤')], max_length=10)),
                ('drink', models.PositiveIntegerField(choices=[(0, '안 마셔요'), (1, '한 잔만!'), (2, '마실래요')])),
                ('member_count', models.PositiveIntegerField(choices=[(1, '혼자'), (2, '둘이서'), (3, '3~4명'), (4, '5인 이상')])),
                ('comment_count', models.PositiveIntegerField(default=0)),
                ('description', models.TextField(null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='posts', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Scrap',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='feed.Post')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='scraps', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('place_img', models.URLField(null=True)),
                ('visit_flag', models.BooleanField(default=False)),
                ('description', models.TextField(null=True)),
                ('select_flag', models.BooleanField(default=False)),
                ('place', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='feed.Place')),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='feed.Post')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
