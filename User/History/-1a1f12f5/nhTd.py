from .imports import *


class GPSList(APIView):
    # permlist = {
    #     'GET': [['client.view_user']],
    # }
    # permission_classes = [IsAdminUser, ApiPermissionCheck]
    permission_classes = [IsAgencyOrAdminUser]
    http_method_names = ['get']
    versioning_class = ApiVersion

    # @swagger_auto_schema(responses={200: GPSSerializer(many=True)})
    def get(self, request):
        agency = Agency.objects.get(user=request.user)
        query_params: QueryDict = request.GET.copy()
        query_params['agency'] = agency.id

        factory = APIRequestFactory()
        agency_request = factory.get(
            "/v2/api/admin_v2/gps/list/",
            query_params,
            HTTP_AUTHORIZATION=request.META.get("HTTP_AUTHORIZATION"),
        )
        agency_request.user = request.user
        agency_request.session = request.session

        view = AdminGPSList.as_view()
        return view(agency_request)
