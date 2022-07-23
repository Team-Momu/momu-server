# Generated by Django 3.0.8 on 2022-07-23 01:30

from django.db import migrations, models
import django.db.models.deletion
import user.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
    ]

    operations = [
        migrations.CreateModel(
            name='Mbti',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mbti', models.CharField(max_length=10)),
                ('type', models.CharField(max_length=10)),
                ('description', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('kakao_id', models.TextField()),
                ('nickname', models.CharField(max_length=30, null=True, unique=True)),
                ('profile_img', models.TextField(null=True)),
                ('level', models.PositiveIntegerField(default=5)),
                ('select_count', models.PositiveIntegerField(default=0)),
                ('refresh_token', models.TextField(null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('is_superuser', models.BooleanField(default=False)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('mbti', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='user.Mbti')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'managed': True,
            },
            managers=[
                ('objects', user.models.UserManager()),
            ],
        ),
    ]
