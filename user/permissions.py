import jwt
from django.shortcuts import get_object_or_404
from rest_framework import permissions, exceptions
from .models import User

from momu.settings import env


class UserPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.COOKIES.get('access_token'):
            access_token = request.COOKIES['access_token']
            payload = jwt.decode(access_token, env('DJANGO_SECRET_KEY'), algorithms=['HS256'])
            user = get_object_or_404(User, pk=payload['user_id'])
            request.user = user
            return True
        else:
            raise exceptions.AuthenticationFailed(detail='토큰 재발급이 필요합니다')

    def has_object_permission(self, request, view, obj):
        if request.COOKIES.get('access_token'):
            access_token = request.COOKIES['access_token']
            payload = jwt.decode(access_token, env('DJANGO_SECRET_KEY'), algorithms=['HS256'])
            user = get_object_or_404(User, pk=payload['user_id'])
            request.user = user
            return True
        else:
            raise exceptions.AuthenticationFailed(detail='토큰 재발급이 필요합니다')
