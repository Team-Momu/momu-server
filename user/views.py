import requests
from django.http import JsonResponse
from django.shortcuts import redirect
from django.core import signing
from django.contrib.auth import get_user_model
from rest_framework import views
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from rest_framework_simplejwt.tokens import RefreshToken
from user.serializers import *

from momu.settings import KAKAO_CONFIG

User = get_user_model()


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
			return Response(status=HTTP_400_BAD_REQUEST)

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
		# user_info = user_info_response.get('kakao_account')
		if not kakao_id:
			return Response(user_info_response, status=HTTP_400_BAD_REQUEST)

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

		momu_token = RefreshToken.for_user(user)
		refresh_token = str(momu_token)
		access_token = str(momu_token.access_token)

		signer = signing.Signer(salt='salt')
		hashed_refresh = signer.sign(refresh_token)

		refresh_data = {
			'kakao_id': kakao_id,
			'refresh_token': hashed_refresh,
		}
		refresh_serializer = UserSerializer(user, data=refresh_data)
		refresh_serializer.is_valid(raise_exception=True)
		refresh_serializer.save()

		response = JsonResponse({
			'message': message,
			'user': user.id,
		}, status=status_code)

		response.set_cookie('access_token', access_token, httponly=True)
		response.set_cookie('refresh_token', refresh_token, httponly=True)

		return response
