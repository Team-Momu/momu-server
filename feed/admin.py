from django.contrib import admin
from feed.models import *


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'location']
    list_display_links = ['id']


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ['id', 'place_name', 'place_id', 'category_name']
    list_display_links = ['id', 'place_name', 'place_id']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'post']
    list_display_links = ['id']


@admin.register(Scrap)
class ScrapAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'post']
    list_display_links = ['id']
