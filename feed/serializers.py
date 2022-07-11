from .models import Post, Place, Comment, Scrap
from user.serializers import ProfileSerializer
from rest_framework import serializers


class PlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Place
        fields = ['id', 'place_id', 'place_name', 'category_name', 'phone',
                  'road_address_name', 'region', 'place_x', 'place_y', 'place_url']


class ScrapSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scrap
        fields = ['id', 'user', 'post']


class CommentSerializer(serializers.ModelSerializer):
    user = ProfileSerializer(read_only=True)
    place = PlaceSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'user', 'post', 'place', 'place_img', 'visit_flag', 'description', 'select_flag']


class PostSerializer(serializers.ModelSerializer):
    user = ProfileSerializer(read_only=True)
    scrap_flag = serializers.BooleanField(default=False)
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'user', 'location', 'time', 'drink', 'member_count',
                  'comment_count', 'description', 'selected_flag', 'scrap_flag', 'comments']
