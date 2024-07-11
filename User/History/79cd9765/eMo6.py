from rest_framework.views import APIView
from rest_framework.permissions import *
from rest_framework.response import Response
from rest_framework.status import *
from rest_framework.test import APIRequestFactory
from drf_yasg.utils import swagger_auto_schema
from django.db.models import Q, Prefetch
from django.http import QueryDict

from library.api_permission_check import ApiPermissionCheck
from library.api_list_pagination import ALP
from library.api_list_pagination_mongo import ALPMongo
from library.mongo import PyMongo
from library.ISODate import *
from library.rayan_permissions import *
from library.api_version import ApiVersion

import bson
import datetime

from agency.models import Agency, User
from ..serializers import *
from car.models import ActiveDevice
from gps.models import Device, Sim, Operator
from gps.admin_v2.brand import BrandList as AdminBrandList

