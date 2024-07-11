from .imports import *


class LatencyApi(ModelViewSet):
    lookup_field = 'id'
    lookup_url_kwarg = 'id'
    http_method_names = ['get', 'put', 'post', 'patch', 'delete']
    permission_classes = [IsAdminUser]
    serializer_class = ReadLatencySerializer
    filter_backends = [CustomFilterBackend, CustomOrderingFilter, SearchFilter]
    filterset_fields = {
        'name': ['icontains'],
        'command': ['icontains'],
        'id': ['exact'],
        'parent': ['exact', 'isnull'],
        # 'type': ['exact'],
    }
    search_fields = ['name', 'command']
    ordering_fields = ['id', 'name']
    ordering = ['-id']
    pagination_class = CustomPagination
    queryset = Latency.objects.select_related("parent").prefetch_related(
        Prefetch(
            lookup='powersys_set',
            queryset=PowerSys.objects.filter(deleted=None, parent__isnull=False)
        )
    ).filter(deleted=None)
    swagger_tags = ['PowerSys Admin']

    def get_object(self):
        # Perform the lookup filtering.
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        assert lookup_url_kwarg in self.kwargs, (
                'Expected view %s to be called with a URL keyword argument '
                'named "%s". Fix your URL conf, or set the `.lookup_field` '
                'attribute on the view correctly.' %
                (self.__class__.__name__, lookup_url_kwarg)
        )

        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        obj: PowerSys = self.queryset.filter(**filter_kwargs).first()
        if obj is None:
            raise CustomException('یافت نشد', 'msg', 404)
        return obj

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return self.read_serializer_class
        return super(LatencyApi, self).get_serializer_class()

    @action(methods=['get'], detail=False, url_path="types")
    def types(self, request, *args, **kwargs):
        return ALP.choices_list(PowerSys.TYPE_CHOICES)

    def create(self, request, *args, **kwargs):
        super(LatencyApi, self).create(request, *args, **kwargs)
        return Response({'msg': "با موفقیت ساخته شد"}, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        super(LatencyApi, self).update(request, *args, **kwargs)
        return Response({'msg': "با موفقیت بروزرسانی شد"}, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        return Response({"msg": 'فعلا در دسترس نیست'}, status=status.HTTP_400_BAD_REQUEST)
