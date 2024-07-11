from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema
from django.db.models import Prefetch

from book.models import Book, Catalogue, Content, Lang, Tag

from library.custom_pagination_class import CustomPagination
from library.drf_filters import CustomFilterBackend, CustomOrderingFilter
from library.drf_exception import CustomException
from library.api_list_pagination import ALP
from helper.response import success

from .serializer.book_serializer import ReadBookSerializer, WriteBookSerializer

# from .serializer.content_serializer import WriteContentSerializer, ReadContentSerializer
# from .serializer.catalogue_serializer import ReadCatalogueSerializer, WriteCatalogueSerializer
# from .serializer.lang_serializer import WriteLangSerializer, ReadLangSerializer
# from .serializer.tag_serializer import WriteTagSerializer, ReadTagSerializer

import re
