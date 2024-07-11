from .imports import *


class BrandList(APIView):
    permlist = {
        'GET': [['gps.view_brand']],
    }
    permission_classes = [IsAgencyOrAdminUser]

    # @swagger_auto_schema(responses={200: UserAdminDto(many=True)})
    def get(self, request):
        factory = APIRequestFactory()
        agency_request = factory.get(
            "/v2/api/admin_v2/brand/list/",
            HTTP_AUTHORIZATION=request.META.get("HTTP_AUTHORIZATION"),
        )
        agency_request.user = request.user
        agency_request.session = request.session

        view = AdminGPSList.as_view()
        return view(agency_request)
