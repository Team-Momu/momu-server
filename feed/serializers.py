from .models import Post, Place, Comment, Scrap
from user.serializers import ProfileSerializer
from rest_framework import serializers


class PlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Place
        fields = ['id', 'place_id', 'place_name', 'category_name', 'phone',
                  'road_address_name', 'region', 'place_x', 'place_y', 'place_url']


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'user', 'post', 'place', 'place_img', 'visit_flag', 'description', 'select_flag']
