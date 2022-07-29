import requests
import jwt
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework import views
from rest_framework.pagination import CursorPagination
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, \
    HTTP_403_FORBIDDEN
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer

from .serializers import *
from user.permissions import UserPermission
from feed.models import Post, Scrap
from .s3storages import s3client
from feed.pagination import PaginationHandlerMixin
from momu.settings import KAKAO_CONFIG, env
from .utils import *

User = get_user_model()


class PostPagination(CursorPagination):
    ordering = '-created_at'


class KakaoAuthorizeView(views.APIView):
    # 인가코드 요청 (프론트 처리 파트)
    def get(self, request):
        rest_api_key = KAKAO_CONFIG['KAKAO_REST_API_KEY']
        redirect_uri = KAKAO_CONFIG['KAKAO_REDIRECT_URI']
        kakao_auth_api = 'https://kauth.kakao.com/oauth/authorize?response_type=code'
        return redirect(
            f'{kakao_auth_api}&client_id={rest_api_key}&redirect_uri={redirect_uri}'
        )


class KakaoView(views.APIView):
    # 회원가입, 로그인
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

        # 서비스 자체 토큰 생성
        momu_token = TokenObtainPairSerializer.get_token(user)
        refresh_token = str(momu_token)
        access_token = str(momu_token.access_token)

        refresh_data = {
            'kakao_id': kakao_id,
            'refresh_token': Encrypt(refresh_token),
        }
        refresh_serializer = UserSerializer(user, data=refresh_data)
        refresh_serializer.is_valid(raise_exception=True)
        refresh_serializer.save()

        response = Response({
            'message': message,
            'user': user.id,
            'access_token': access_token,
            'refresh_token': refresh_token,
        }, status=status_code)

        # response.set_cookie('access_token', access_token, httponly=True, domain='momueat.com', samesite=None, secure=True)
        # response.set_cookie('refresh_token', refresh_token, httponly=True, domain='momueat.com', samesite=None, secure=True)
        response.set_cookie('access_token', access_token, httponly=True)
        response.set_cookie('refresh_token', refresh_token, httponly=True)

        return response


class ProfileUpdateView(views.APIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    # 프로필 조회
    def get(self, request):
        user = request.user
        serializer = self.serializer_class(user)

        return Response({'message': '프로필 조회 성공', 'data': serializer.data}, status=HTTP_200_OK)

    # 프로필 설정
    def put(self, request):
        user = request.user
        filename = request.FILES.get('profile_img')
        request_data = {
            'nickname': request.data['nickname'],
            'profile_img': None
        }
        if filename:
            # 프로필 이미지 업로드
            url = s3client.upload(filename)
            if not url:
                return Response({'message': '이미지 업로드 실패'}, status=HTTP_400_BAD_REQUEST)
            request_data['profile_img'] = url

        serializer = self.serializer_class(user, data=request_data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': '프로필 설정 성공',
                'data': serializer.data,
            }, status=HTTP_200_OK)
        else:
            return Response({'message': '잘못된 형식의 요청입니다'}, status=HTTP_400_BAD_REQUEST)


class RefreshTokenView(views.APIView):
    # 로그인 연장
    def post(self, request):
        try:
            refresh_token = request.COOKIES.get('refresh_token')
            if not refresh_token:
                return Response({'message': '로그인이 필요합니다'}, status=HTTP_401_UNAUTHORIZED)

            payload = jwt.decode(refresh_token, env('DJANGO_SECRET_KEY'), algorithms=['HS256'])
            user = get_object_or_404(User, pk=payload['user_id'])
            if not VerifyToken(user.refresh_token, refresh_token):
                return Response({'message': '토큰 재발급 권한이 없습니다'}, status=HTTP_403_FORBIDDEN)

            # 토큰 재발급
            refresh_data = {'refresh': refresh_token}
            serializer = TokenRefreshSerializer(data=refresh_data)
            serializer.is_valid(raise_exception=True)

            user.refresh_token = Encrypt(serializer.data['refresh'])
            user.save()

            response = Response({
                'message': '토큰 재발급 성공',
                'user': user.id,
            }, status=HTTP_201_CREATED)

            # response.set_cookie('access_token', serializer.data['access'], httponly=True, domain='momueat.com', samesite=None, secure=True)
            # response.set_cookie('refresh token', serializer.data['refresh'], httponly=True, domain='momueat.com', samesite=None, secure=True)
            response.set_cookie('access_token', serializer.data['access'], httponly=True)
            response.set_cookie('refresh token', serializer.data['refresh'], httponly=True)
            return response

        # 리프레시 토큰 만료
        except(jwt.exceptions.ExpiredSignatureError):
            if user:
                user.refresh_token = None
                user.save()
            return Response({'message': '토큰이 만료되어 로그인이 필요합니다'}, status=HTTP_401_UNAUTHORIZED)

        # invalid 한 토큰
        except(jwt.exceptions.InvalidTokenError):
            if user:
                user.refresh_token = None
                user.save()
            response = Response({'message': '로그인이 필요합니다'}, status=HTTP_401_UNAUTHORIZED)
            response.delete_cookie('refresh_token')

            return response


class MbtiView(views.APIView):
    permission_classes = [IsAuthenticated]

    # 먹BTI 설정
    def post(self, request):
        mbti = request.data['mbti']

        if Mbti.objects.filter(mbti=mbti).exists():
            mbti_object = Mbti.objects.get(mbti=mbti)
            serializer = MbtiSerializer(mbti_object)

            user = request.user
            user.mbti = mbti_object
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
    permission_classes = [IsAuthenticated]

    # 내가 작성한 큐레이션 목록 조회
    def get(self, request):
        user = request.user
        user_serializer = ProfileSerializer(user)

        posts = Post.objects.filter(user_id=user)

        cursor = self.paginate_queryset(posts)
        for c in cursor:
            if Scrap.objects.filter(post=c, user=user).exists():
                c.scrap_flag = True

        if cursor is not None:
            post_serializer = self.get_paginated_response(ProfilePostSerializer(cursor, many=True).data)
        else:
            post_serializer = ProfilePostSerializer(posts, many=True)

        return Response(
            {'message': '직성한 글 목록 조회 성공', 'data': {'profile': user_serializer.data, 'post': post_serializer.data}},
            status=HTTP_200_OK)


class ProfileScrapView(views.APIView, PaginationHandlerMixin):
    pagination_class = PostPagination
    permission_classes = [IsAuthenticated]

    # 내가 스크랩한 큐레이션 목록 조회
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
