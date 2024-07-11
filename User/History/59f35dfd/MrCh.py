from .imports import *


@extend_schema(tags=["Book"])
class BookApi(ModelViewSet):
    lookup_field = "id"
    lookup_url_kwarg = "id"
    http_method_names = ["get", "put", "post", "patch"]
    permission_classes = [IsAdminUser]
    serializer_class = WriteBookSerializer
    read_serializer_class = ReadBookSerializer
    filter_backends = [CustomFilterBackend, CustomOrderingFilter, SearchFilter]
    filterset_fields = {
        "title": ["icontains"],
        "writer": ["icontains"],
        "editor": ["icontains"],
        "publisher": ["icontains"],
        "lang__name": ["icontains"],
        "id": ["exact"],
        "cover_count": ["exact"],
        "cover_number": ["exact"],
    }
    search_fields = ["title", "writer", "editor", "publisher", "subject"]
    ordering_fields = ["id", "created_at", "updated_at", "cover_count"]
    ordering = ["-id"]
    pagination_class = CustomPagination
    queryset = Book.objects.select_related("lang").filter(deleted_at=None)

    def get_object(self):
        # Perform the lookup filtering.
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        assert lookup_url_kwarg in self.kwargs, (
            "Expected view %s to be called with a URL keyword argument "
            'named "%s". Fix your URL conf, or set the `.lookup_field` '
            "attribute on the view correctly."
            % (self.__class__.__name__, lookup_url_kwarg)
        )

        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        obj = self.queryset.filter(**filter_kwargs).first()
        if obj is None:
            raise CustomException("یافت نشد", "msg", 404)
        return obj

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            self.queryset = self.get_queryset().prefetch_related(
                Prefetch(
                    lookup="catalogue_set",
                    queryset=Catalogue.objects.filter(deleted_at=None),
                )
            )
            return self.read_serializer_class
        return super(BookApi, self).get_serializer_class()

    def destroy(self, request, *args, **kwargs):
        return Response("فعلا در دسترس نیست", status=status.HTTP_400_BAD_REQUEST)
