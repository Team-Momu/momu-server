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
    post_user = serializers.SerializerMethodField()
    place = PlaceSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'user', 'post', 'post_user', 'place', 'place_img', 'description', 'select_flag', 'created_at']

    def get_post_user(self, obj):
        return obj.post.user.id


class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'user', 'post', 'place', 'place_img', 'description', 'created_at']


class PostDetailSerializer(serializers.ModelSerializer):
    user = ProfileSerializer(read_only=True)
    scrap_flag = serializers.BooleanField(default=False)
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'user', 'created_at', 'location', 'time', 'drink', 'member_count',
                  'comment_count', 'description', 'selected_flag', 'scrap_flag', 'comments']


class PostListSerializer(serializers.ModelSerializer):
    user = ProfileSerializer(read_only=True)
    scrap_flag = serializers.BooleanField(default=False)

    class Meta:
        model = Post
        fields = ['id', 'user', 'created_at', 'location', 'time', 'drink', 'member_count',
                  'comment_count', 'description', 'selected_flag', 'scrap_flag']


class PostCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['id', 'user', 'location', 'time', 'drink', 'member_count',
                  'comment_count', 'description', 'selected_flag']
