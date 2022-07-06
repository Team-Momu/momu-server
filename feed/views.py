import requests

from django.shortcuts import get_object_or_404
from django.http import JsonResponse, QueryDict
from rest_framework import views
from rest_framework.status import *
from rest_framework.response import Response
from .models import Post, Place, Comment, Scrap
from .serializers import PlaceSerializer
from momu.settings import KAKAO_CONFIG


class PlaceView(views.APIView):
    serializer_class = PlaceSerializer

    def get(self, request):
        if 'keyword' in request.GET:
            keyword = request.GET.get('keyword')
            rest_api_key = KAKAO_CONFIG['KAKAO_REST_API_KEY']

            url = 'https://dapi.kakao.com/v2/local/search/keyword.json'
            params = {'query': keyword, 'address_name': '서대문구', 'category_group_code': 'CE7', 'page': 1}
            headers = {'Authorization': 'KakaoAK '+rest_api_key}

            data = requests.get(url, params=params, headers=headers).json()['documents']

            return Response({'message': '식당 검색 성공', 'data': data}, status=HTTP_200_OK)

        return Response(status=HTTP_400_BAD_REQUEST)


    def post(self, request):
        request.data._mutable = True
        data = self.request.data
        data['region'] = data['region'].split()[2]
        data['category_name'] = data['category_name'].split(' > ')[1]

        serializer = self.serializer_class(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response({'message': '식당 저장 성공', 'data': serializer.data}, status=HTTP_201_CREATED)

        else:
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)