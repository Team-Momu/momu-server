from django.contrib.auth import get_user_model
from .models import Mbti
from rest_framework import serializers

User = get_user_model()


class MbtiSerializer(serializers.ModelSerializer):
	class Meta:
		model = Mbti
		fields = ['id', 'mbti', 'description']


class UserSerializer(serializers.ModelSerializer):
	mbti_name = serializers.SerializerMethodField()
	mbti_description = serializers.SerializerMethodField()

	class Meta:
		model = User
		fields = ['id', 'kakao_id', 'nickname', 'profile_img', 'mbti', 'mbti_name', 'mbti_description', 'level', 'select_count', 'refresh_token']

	def get_mbti_name(self, obj):
		return obj.mbti.mbti

	def get_mbti_description(self, obj):
		return obj.mbti.description
