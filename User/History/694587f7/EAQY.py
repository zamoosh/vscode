from django.urls import path
from . import *

urlpatterns = [
    path("list/", BrandList.as_view()),
]
