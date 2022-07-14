from django.contrib.auth import get_user_model
from .models import Mbti
from rest_framework import serializers
from feed.models import Post

User = get_user_model()


class MbtiSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mbti
        fields = ['id', 'mbti', 'type', 'description', 'mbti_img']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'kakao_id', 'select_count', 'refresh_token']


class ProfileSerializer(serializers.ModelSerializer):
    mbti = MbtiSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'nickname', 'profile_img', 'mbti', 'level', 'select_count']


class ProfilePostSerializer(serializers.ModelSerializer):
    user = ProfileSerializer(read_only=True)
    scrap_flag = serializers.BooleanField(default=False)

    class Meta:
        model = Post
        fields = ['id', 'user', 'location', 'time', 'drink', 'member_count',
                  'comment_count', 'description', 'selected_flag', 'scrap_flag']
