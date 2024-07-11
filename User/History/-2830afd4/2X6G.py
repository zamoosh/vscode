from django.urls import path
from rest_framework.routers import DefaultRouter
from . import *


latency_router = DefaultRouter()
latency_router.register()

urlpatterns = [
    path()
]
