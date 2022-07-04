from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from rest_framework import views
from rest_framework.status import *
from rest_framework.response import Response
from .models import Post, Place, Comment, Scrap
from .serializers import PlaceSerializer

