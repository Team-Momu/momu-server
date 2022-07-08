from django.urls import path
from .views import *


app_name = 'feed'

urlpatterns = [
	path('search/', PlaceView.as_view()),
]
