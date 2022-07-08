from django.contrib.auth import get_user_model
from .models import Mbti
from rest_framework import serializers

User = get_user_model()


class MbtiSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mbti
        fields = ['id', 'mbti', 'description']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'kakao_id', 'select_count', 'refresh_token']


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'kakao_id', 'nickname', 'profile_img', 'level', 'select_count', 'refresh_token']
