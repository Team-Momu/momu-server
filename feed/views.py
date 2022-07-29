import requests

from django.shortcuts import get_object_or_404
from rest_framework import views
from rest_framework.status import *
from rest_framework.response import Response
from rest_framework.pagination import CursorPagination

from .models import Post, Place, Comment, Scrap
from user.models import User
from .serializers import PlaceSerializer, CommentSerializer, PostDetailSerializer,\
    PostListSerializer, PostCreateSerializer, ScrapSerializer, CommentCreateSerializer

from .pagination import PaginationHandlerMixin
from user.permissions import UserPermission
from rest_framework.permissions import IsAuthenticated
from momu.settings import KAKAO_CONFIG
from .s3storages import s3client


class PostPagination(CursorPagination):
    ordering = '-created_at'


class CommentPagination(CursorPagination):
    ordering = 'created_at'


class PlaceView(views.APIView):
    serializer_class = PlaceSerializer

    # 식당 검색
    def get(self, request):
        size = 15
        page = request.GET.get('page', 1)

        if 'keyword' not in request.GET or not request.GET.get('keyword'):
            return Response(status=HTTP_400_BAD_REQUEST)

        keyword = request.GET.get('keyword')
        rest_api_key = KAKAO_CONFIG['KAKAO_REST_API_KEY']

        # 카카오맵 장소 검색 요청
        url = 'https://dapi.kakao.com/v2/local/search/keyword.json'
        rect = '126.86417624432379,37.599026970443035,126.962764139611,37.5318164676656'
        params = {'query': keyword, 'category_group_code': 'FD6', 'rect': rect, 'size': size, 'page': page}
        headers = {'Authorization': 'KakaoAK ' + rest_api_key}

        data = requests.get(url, params=params, headers=headers).json()['documents']
        total = requests.get(url, params=params, headers=headers).json()['meta']['total_count']

        return Response({'message': '식당 검색 성공', 'data': data, 'page': page, 'total': total}, status=HTTP_200_OK)

    """
    def post(self, request):
        request.data._mutable = True

        data = request.data
        data['region'] = data['region'].split()[2]
        data['category_name'] = data['category_name'].split(' > ')[1]

        if Place.objects.filter(place_id=data['place_id']).exists():
            place_object = Place.objects.get(place_id=data['place_id'])
            place_id = self.serializer_class(place_object).data['id']
            return Response({'message': '이미 존재하는 식당', 'place_id': place_id}, status=HTTP_200_OK)

        else:
            serializer = self.serializer_class(data=data)

            if serializer.is_valid():
                serializer.save()
                return Response({'message': '식당 저장 성공', 'place_id': serializer.data['id']}, status=HTTP_201_CREATED)

            else:
                return Response({'message': '잘못된 형식의 요청입니다'}, serializer.errors, status=HTTP_400_BAD_REQUEST)
    """


class PostListView(views.APIView, PaginationHandlerMixin):
    pagination_class = PostPagination
    permission_classes = [IsAuthenticated]

    # 큐레이션 전체 목록 조회
    def get(self, request):
        user = request.user

        # 필터링
        location = request.GET.get('location')
        time = request.GET.get('time')
        drink = request.GET.get('drink')
        member_count = request.GET.get('member_count')

        params = {'location': location, 'time': time, 'drink': drink, 'member_count': member_count}
        arguments = {}
        for key, value in params.items():
            if value:
                arguments[key] = value

        posts = Post.objects.filter(**arguments)
        cursor = self.paginate_queryset(posts)
        for c in cursor:
            if Scrap.objects.filter(post=c, user=user).exists():
                c.scrap_flag = True

        if cursor is not None:
            serializer = self.get_paginated_response(PostListSerializer(cursor, many=True).data)
        else:
            serializer = PostListSerializer(posts, many=True)

        return Response({'message': '게시글 조회 성공', 'data': serializer.data}, status=HTTP_200_OK)

    # 큐레이션 생성
    def post(self, request):
        user = request.user
        post_data = {
            'user': user, 'location': request.data['location'], 'time': request.data['time'], 'drink': request.data['drink'],
            'member_count': request.data['member_count'], 'description': request.data['description']
        }
        serializer = PostCreateSerializer(data=post_data)

        if serializer.is_valid():
            serializer.save()
            return Response({'message': '게시글 등록 성공', 'data': serializer.data}, status=HTTP_201_CREATED)
        return Response({'message': '잘못된 형식의 요청입니다: 게시글 정보', 'data': serializer.errors}, status=HTTP_400_BAD_REQUEST)


class PostDetailView(views.APIView):
    serializer_class = PostDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_object_post(self, pk):
        return get_object_or_404(Post, pk=pk)

    # 큐레이션 상세 조회
    def get(self, request, pk):
        post = self.get_object_post(pk)
        serializer = self.serializer_class(post)

        return Response({'message': '게시글 상세 조회 성공', 'data': serializer.data}, status=HTTP_200_OK)


class CommentView(views.APIView, PaginationHandlerMixin):
    pagination_class = CommentPagination
    permission_classes = [IsAuthenticated]

    def get_object_post(self, pk):
        return get_object_or_404(Post, pk=pk)

    # 답변 목록 조회
    def get(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        comments = Comment.objects.filter(post_id=post.id)

        cursor = self.paginate_queryset(comments)
        if cursor is not None:
            serializer = self.get_paginated_response(CommentSerializer(cursor, many=True).data)
            return Response({
                'message': '답변 조회 성공',
                'data': serializer.data,
            }, status=HTTP_200_OK)
        else:
            serializer = CommentSerializer(comments)
            return Response({
                'message': '답변 조회 성공',
                'data': serializer.data['comments'],
            }, status=HTTP_200_OK)

    # 답변 생성
    def post(self, request, pk):
        # 식당 등록
        place_data = request.data['place']
        place_id = place_data['id']
        if not Place.objects.filter(place_id=place_id).exists():
            place_request_data = {
                'place_id': place_id,
                'place_name': place_data['place_name'],
                'category_name': place_data['category_name'].split(' > ')[1],
                'phone': place_data['phone'],
                'road_address_name': place_data['road_address_name'],
                'region': place_data['address_name'].split()[2],
                'place_x': place_data['x'],
                'place_y': place_data['y'],
                'place_url': place_data['place_url']
            }
            place_serializer = PlaceSerializer(data=place_request_data)
            if place_serializer.is_valid():
                place_serializer.save()
                place = place_serializer.data['id']
            else:
                return Response({'message': '잘못된 형식의 요청입니다: 식당 정보'}, status=HTTP_400_BAD_REQUEST)
        else:
            place_object = Place.objects.get(place_id=place_id)
            place = place_object.id

        # 답글 등록
        filename = request.FILES.get('place_img')
        comment_data = {
            'user': request.user.id,
            'post': pk,
            'place': place,
            'place_img': None,
            'description': request.data['description']
        }
        if filename:
            # 이미지 업로드
            url = s3client.upload(filename)
            if not url:
                return Response({'message': '이미지 업로드 실패'}, status=HTTP_400_BAD_REQUEST)
            comment_data['place_img'] = url

        comment_serializer = CommentCreateSerializer(data=comment_data)

        if comment_serializer.is_valid():
            comment_serializer.save()

            post = self.get_object_post(pk=pk)
            post.comment_count += 1
            post.save()

            return Response({
                'message': '답글 등록 성공',
                'data': comment_serializer.data,
            }, status=HTTP_200_OK)
        else:
            return Response({'message': '잘못된 형식의 요청입니다: 답글 정보'}, status=HTTP_400_BAD_REQUEST)


class ScrapView(views.APIView):
    serializer_class = ScrapSerializer
    permission_classes = [IsAuthenticated]

    # 스크랩 생성
    def post(self, request):
        user = request.user

        if not request.data or not request.data['post']:
            return Response({'message': '잘못된 형식의 요청입니다: post'}, status=HTTP_408_REQUEST_TIMEOUT)

        scrap_data = {'post': request.data['post'], 'user': user}
        serializer = self.serializer_class(data=scrap_data)

        if serializer.is_valid():
            serializer.save()
            return Response({'message': '스크랩 성공', 'data': serializer.data}, status=HTTP_201_CREATED)
        return Response({'message': '잘못된 형식의 요청입니다', 'data': serializer.errors}, status=HTTP_400_BAD_REQUEST)

    # 스크랩 취소
    def delete(self, request):
        user = request.user
        post = request.data['post']

        Scrap.objects.filter(user=user, post=post).delete()

        return Response({'message': '스크랩 취소 성공 '}, status=HTTP_200_OK)


class CommentSelectView(views.APIView):
    def get_object_post(self, pk):
        return get_object_or_404(Post, pk=pk)

    def get_object_comment(self, pk):
        return get_object_or_404(Comment, pk=pk)

    def get_object_user(self, pk):
        return get_object_or_404(User, pk=pk)

    # 답변 채택
    def post(self, request, post_pk, comment_pk):
        post = self.get_object_post(pk=post_pk)
        comment = self.get_object_comment(pk=comment_pk)

        # if int(str(post.user)) != request.user.id:
        if int(str(post.user)) != 1:
            return Response({'message': '해당 게시글에서 답변을 채택할 권한이 없습니다'}, status=HTTP_403_FORBIDDEN)
        if post.selected_flag:
            return Response({'message': '이미 답변이 채택된 큐레이션입니다'}, status=HTTP_409_CONFLICT)

        post.selected_flag = True
        comment.select_flag = True
        author = self.get_object_user(pk=int(str(comment.user)))
        author.select_count += 1
        comment.save()
        author.save()
        post.save()
        return Response({'message': '답글 채택 성공'}, status=HTTP_201_CREATED)

    # 채택 취소
    def delete(self, request, post_pk, comment_pk):
        post = self.get_object_post(pk=post_pk)
        comment = self.get_object_comment(pk=comment_pk)

        # if int(str(post.user)) != request.user.id:
        if int(str(post.user)) != 1:
            return Response({'message': '해당 게시글에서 답글 채택을 취소할 권한이 없습니다'}, status=HTTP_403_FORBIDDEN)
        if not comment.select_flag:
            return Response({'message': '해당 답글이 채택되어 있지 않습니다'}, status=HTTP_400_BAD_REQUEST)

        post.selected_flag = False
        comment.select_flag = False
        author = self.get_object_user(pk=int(str(comment.user)))
        author.select_count -= 1
        comment.save()
        author.save()
        post.save()
        return Response({'message': '답글 채택 취소 성공'}, status=HTTP_200_OK)
