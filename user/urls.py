from django.urls import path
from django.conf.urls import url
from .views import *


app_name = 'user'

urlpatterns = [
	# TO REMOVE
	path('kakao/authorize', KakaoAuthorizeView.as_view()),
	path('kakao', KakaoView.as_view()),
	# path('profile', ProfileView.as_view({'get': 'list'})),
	path('profile/<int:pk>', ProfileUpdateView.as_view()),
]
