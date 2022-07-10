from django.urls import path
from .views import *


app_name = 'feed'

urlpatterns = [
    path('', PostListView.as_view()),
    path('search/', PlaceView.as_view()),
    path('<int:pk>/', PostDetailView.as_view()),
    path('<int:pk>/comment/', CommentView.as_view()),
    path('<int:post_pk>/select/<int:comment_pk>/', CommentSelectView.as_view()),
]
