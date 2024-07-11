from .imports import *


class BrandList(APIView):
    permlist = {
        'GET': [['gps.view_brand']],
    }
    permission_classes = [IsAdminUser, ApiPermissionCheck]
    # permission_classes = [IsAdminUser]

    # @swagger_auto_schema(responses={200: UserAdminDto(many=True)})
    def get(self, request):
        agency = Agency.objects.get(user=request.user)
        query_params: QueryDict = request.GET.copy()
        query_params['agency'] = agency.id

        factory = APIRequestFactory()
        agency_request = factory.get(
            "/v2/api/admin_v2/brand/list/",
            query_params,
            HTTP_AUTHORIZATION=request.META.get("HTTP_AUTHORIZATION"),
        )
        agency_request.user = request.user
        agency_request.session = request.session

        view = AdminGPSList.as_view()
        return view(agency_request)
