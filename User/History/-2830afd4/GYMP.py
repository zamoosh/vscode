from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import *


latency_router = DefaultRouter()
latency_router.register("", LatencyApi)

urlpatterns = [
    path("", include(latency_router.urls))
]
