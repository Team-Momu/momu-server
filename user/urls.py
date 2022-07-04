from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView
from .views import *


app_name = 'user'

urlpatterns = [
	# TO REMOVE
	path('kakao/authorize', KakaoAuthorizeView.as_view()),
	path('kakao', KakaoView.as_view()),
]
