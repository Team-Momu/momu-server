from django.urls import path
from rest_framework_simplejwt.views import TokenVerifyView
from .views import *


app_name = 'user'

urlpatterns = [
    # TO REMOVE
    path('kakao/authorize/', KakaoAuthorizeView.as_view()),
    path('kakao/', KakaoView.as_view()),
    path('token/refresh/', RefreshTokenView.as_view()),
    path('token/verify/', TokenVerifyView.as_view()),
    path('profile/<int:pk>/', ProfileUpdateView.as_view()),
    path('profile/<int:pk>/post/', ProfilePostView.as_view()),
    path('types', MbtiView.as_view()),
]
