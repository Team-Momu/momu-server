import requests
import jwt
from django.shortcuts import redirect, get_object_or_404
from django.core import signing
from django.contrib.auth import get_user_model
from rest_framework import views
from rest_framework.pagination import CursorPagination
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, \
    HTTP_403_FORBIDDEN
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import UpdateModelMixin
from user.serializers import *
from user.permissions import UserPermission
from feed.models import Post, Scrap

from feed.pagination import PaginationHandlerMixin
from momu.settings import KAKAO_CONFIG, env

User = get_user_model()


class PostPagination(CursorPagination):
    ordering = '-created_at'


# TO REMOVE : 프론트 처리 파트 -> 인가 코드
class KakaoAuthorizeView(views.APIView):
    def get(self, request):
        rest_api_key = KAKAO_CONFIG['KAKAO_REST_API_KEY']
        redirect_uri = KAKAO_CONFIG['KAKAO_REDIRECT_URI']
        kakao_auth_api = 'https://kauth.kakao.com/oauth/authorize?response_type=code'
        return redirect(
            f'{kakao_auth_api}&client_id={rest_api_key}&redirect_uri={redirect_uri}'
        )


class KakaoView(views.APIView):
    def get(self, request):
        code = request.GET.get('code')
        if not code:
            return Response({'message': '인가코드를 전달받지 못했습니다'}, status=HTTP_400_BAD_REQUEST)

        # 토큰 받기
        kakao_token_api = 'https://kauth.kakao.com/oauth/token'
        token_data = {
            'grant_type': 'authorization_code',
            'client_id': KAKAO_CONFIG['KAKAO_REST_API_KEY'],
            'redirect_uri': KAKAO_CONFIG['KAKAO_REDIRECT_URI'],
            'code': code,
            'client_secret': KAKAO_CONFIG['KAKAO_CLIENT_SECRET_KEY'],
        }
        token_headers = {
            'Content-type': 'application/x-www-form-urlencoded;charset=utf-8'
        }

        token_response = requests.post(kakao_token_api, data=token_data, headers=token_headers).json()

        # 토큰으로 사용자 정보 가져오기
        kakao_access_token = token_response.get('access_token')
        kakao_user_info_api = 'https://kapi.kakao.com/v2/user/me'
        user_info_headers = {
            'Authorization': f'Bearer {kakao_access_token}',
            'Content-type': 'application/x-www-form-urlencoded;charset=utf-8',
        }

        user_info_response = requests.get(kakao_user_info_api, headers=user_info_headers).json()

        kakao_id = user_info_response.get('id')
        if not kakao_id:
            return Response({'message': '카카오 유저 정보를 받아올 수 없습니다'}, status=HTTP_400_BAD_REQUEST)

        user_data = {'kakao_id': kakao_id}
        try:
            # 로그인
            kakao_user = User.objects.get(kakao_id=kakao_id)
            # TO FIX : 개선 필요
            serializer = UserSerializer(kakao_user, data=user_data)
            message = '로그인 성공'
            status_code = HTTP_200_OK
        except User.DoesNotExist:
            # 회원가입
            serializer = UserSerializer(data=user_data)
            message = '회원가입 성공'
            status_code = HTTP_201_CREATED

        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        momu_token = TokenObtainPairSerializer.get_token(user)
        refresh_token = str(momu_token)
        access_token = str(momu_token.access_token)

        # TO FIX : 암호화 로직
        # salt = uuid.uuid4()
        # signer = signing.Signer(salt)
        # hashed_refresh = signer.sign(refresh_token)

        refresh_data = {
            'kakao_id': kakao_id,
            'refresh_token': refresh_token,
        }
        refresh_serializer = UserSerializer(user, data=refresh_data)
        refresh_serializer.is_valid(raise_exception=True)
        refresh_serializer.save()

        response = Response({
            'message': message,
            'user': user.id,
            'code': code,
            'token': token_response,
            'info': user_info_response,
        }, status=status_code)

        response.set_cookie('access_token', access_token, httponly=True)
        response.set_cookie('refresh_token', refresh_token, httponly=True)

        return response


class ProfileUpdateView(GenericAPIView, UpdateModelMixin):
    serializer_class = ProfileSerializer
    permission_classes = [UserPermission]
    queryset = User.objects.all()

    def get(self, request):
        user = request.user
        serializer = self.serializer_class(user)

        return Response({'message': '프로필 조회 성공', 'data': serializer.data}, status=HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class RefreshTokenView(views.APIView):
    def post(self, request):
        try:
            refresh_token = request.COOKIES.get('refresh_token')
            if not refresh_token:
                return Response({'message': '로그인이 필요합니다'}, status=HTTP_401_UNAUTHORIZED)

            payload = jwt.decode(refresh_token, env('DJANGO_SECRET_KEY'), algorithms=['HS256'])
            user = get_object_or_404(User, pk=payload['user_id'])

            if user.refresh_token != refresh_token:
                return Response({'message': '토큰 재발급 권한이 없습니다'}, status=HTTP_403_FORBIDDEN)

            refresh_data = {'refresh': request.COOKIES.get('refresh_token')}
            serializer = TokenRefreshSerializer(data=refresh_data)
            serializer.is_valid(raise_exception=True)

            user.refresh_token = serializer.data['refresh']
            user.save()

            response = Response({
                'message': '토큰 재발급 성공',
                'user': user.id,
            }, status=HTTP_201_CREATED)

            response.set_cookie('access_token', serializer.data['access'], httponly=True, samesite=None, secure=True)
            response.set_cookie('refresh token', serializer.data['refresh'], httponly=True, samesite=None, secure=True)
            return response

        # 리프레시 토큰 만료
        except(jwt.exceptions.ExpiredSignatureError):
            if user:
                user.refresh_token = None
                user.save()
            return Response({'message': '토큰이 만료되어 로그인이 필요합니다'}, status=HTTP_401_UNAUTHORIZED)

        # invalid 한 토큰
        except(jwt.exceptions.InvalidTokenError):
            response = Response({'message': '로그인이 필요합니다'}, status=HTTP_401_UNAUTHORIZED)
            response.delete_cookie('refresh_token')

            return response


class MbtiView(views.APIView):
    # TO REMOVE : 개발 중
    # permission_classes = [UserPermission]

    def post(self, request):
        mbti = request.data['mbti']

        if Mbti.objects.filter(mbti=mbti).exists():
            mbti_object = Mbti.objects.get(mbti=mbti)
            serializer = MbtiSerializer(mbti_object)

            user = get_object_or_404(User, pk=request.user.id)
            user.mbti = serializer.data['id']
            user.save()

            return Response({
                'message': '먹BTI 등록 성공',
                'mbti': serializer.data['mbti'],
                'description': serializer.data['description'],
            }, status=HTTP_201_CREATED)
        else:
            return Response({'message': '잘못된 형식의 요청입니다'}, status=HTTP_400_BAD_REQUEST)


class ProfilePostView(views.APIView, PaginationHandlerMixin):
    pagination_class = PostPagination
    permission_classes = [UserPermission]

    def get(self, request):
        user = request.user
        user_serializer = ProfileSerializer(user)

        posts = Post.objects.filter(user_id=user)

        for post in posts:
            if Scrap.objects.filter(post=post.id, user=user).exists():
                post.scrap_flag = True

        cursor = self.paginate_queryset(posts)
        if cursor is not None:
            post_serializer = self.get_paginated_response(ProfilePostSerializer(cursor, many=True).data)
        else:
            post_serializer = ProfilePostSerializer(posts, many=True)

        return Response(
            {'message': '직성한 글 목록 조회 성공', 'data': {'profile': user_serializer.data, 'post': post_serializer.data}},
            status=HTTP_200_OK)


class ProfileScrapView(views.APIView, PaginationHandlerMixin):
    pagination_class = PostPagination
    permission_classes = [UserPermission]

    def get(self, request):
        user = request.user
        user_serializer = ProfileSerializer(user)

        scrap_list = Scrap.objects.filter(user=user).values_list('post')
        posts = Post.objects.filter(id__in=scrap_list)  # 스크랩 한 글 객체 목록

        cursor = self.paginate_queryset(posts)

        for c in cursor:
            c.scrap_flag = True

        if cursor is not None:
            post_serializer = self.get_paginated_response(ProfilePostSerializer(cursor, many=True).data)
        else:
            post_serializer = ProfilePostSerializer(posts, many=True)

        return Response(
            {'message': '스크랩 한 글 목록 조회 성공', 'data': {'profile': user_serializer.data, 'post': post_serializer.data}},
            status=HTTP_200_OK)
