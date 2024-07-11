from django.urls import path
from . import *

urlpatterns = [
    path("list/", GPSList.as_view()),
]
