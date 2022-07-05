import requests

from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from rest_framework import views
from rest_framework.status import *
from rest_framework.response import Response
from .models import Post, Place, Comment, Scrap
from .serializers import PlaceSerializer
from momu.settings import KAKAO_CONFIG


class PlaceView(views.APIView):
    def get(self, request):
        if 'keyword' in request.GET:
            keyword = request.GET.get('keyword')
            rest_api_key = KAKAO_CONFIG['KAKAO_REST_API_KEY']

            url = 'https://dapi.kakao.com/v2/local/search/keyword.json'
            params = {'query': keyword, 'page': 1}
            headers = {'Authorization': 'KakaoAK '+rest_api_key}

            data = requests.get(url, params=params, headers=headers).json()['documents']

            return Response(data, status=HTTP_200_OK)

        return Response(status=HTTP_400_BAD_REQUEST)
