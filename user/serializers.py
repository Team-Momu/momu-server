from django.contrib.auth import get_user_model
from .models import Mbti
from rest_framework import serializers
from feed.models import Post

User = get_user_model()


class MbtiSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mbti
        fields = ['id', 'mbti', 'type', 'description']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'kakao_id', 'refresh_token']


class ProfileSerializer(serializers.ModelSerializer):
    mbti = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'nickname', 'profile_img', 'mbti', 'level', 'select_count']

    def get_mbti(self, obj):
        return obj.mbti.mbti


class ProfilePostSerializer(serializers.ModelSerializer):
    user = ProfileSerializer(read_only=True)
    scrap_flag = serializers.BooleanField(default=False)

    class Meta:
        model = Post
        fields = ['id', 'user', 'location', 'time', 'drink', 'member_count',
                  'comment_count', 'description', 'selected_flag', 'scrap_flag']
