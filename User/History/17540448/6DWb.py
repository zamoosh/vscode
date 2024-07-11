from django.db import transaction
from rest_framework import serializers
from rest_framework import status
from rest_framework.fields import empty
from ...models import Book, Catalogue
from library.drf_exception import CustomException


class ReadCatalogueIdNameSerializer(serializers.ModelSerializer):
    """
    This class is only used in "ReadBookSerializer" class to show the number of catalogues of a Book.
    """

    class Meta:
        model = Catalogue
        fields = ["id", "name"]


class ReadCatalogueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Catalogue
        fields = [
            "id",
            "book",
            "parent",
            "name",
            "slug",
            "sub_name",
            "created_at",
            "updated_at",
            "order",
            "content_count",
        ]

    content_count = serializers.SerializerMethodField()
    parent = serializers.SerializerMethodField()
    book = serializers.SerializerMethodField()

    def get_book(self, obj: Catalogue):
        return {"id": obj.book.id, "name": obj.book.title}

    def get_parent(self, obj: Catalogue):
        if obj.parent is not None:
            return {"name": obj.parent.name, "id": obj.parent.id}
        return None

    def get_content_count(self, obj: Catalogue):
        return obj.content_set.count()


class WriteCatalogueSerializer(serializers.Serializer):
    parent = serializers.IntegerField(allow_null=True)  # Parent's id
    book = serializers.IntegerField()  # Book's id
    name = serializers.CharField(trim_whitespace=True)
    slug = serializers.CharField(allow_null=True)
    sub_name = serializers.CharField(allow_null=True)
    # FIXME: default value is 0, should remove it if needed!
    order = serializers.IntegerField()

    def __init__(self, instance=None, data=empty, **kwargs):
        super(WriteCatalogueSerializer, self).__init__(instance, data, **kwargs)

        # === b is Book === #
        self.b: Book | None = None
        self.parent_obj: Catalogue | None = None

    def to_representation(self, instance):
        return ReadCatalogueSerializer(instance).data

    def update(self, instance: Catalogue, validated_data):
        if instance.parent is not None:
            Catalogue.objects.partial_rebuild(instance.parent.id)

        try:
            if validated_data["parent"] == instance.id:
                raise CustomException(
                    "نمیتوانید یک کاتالوگ را به خودش وصل کنید",
                    "parent",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

            with transaction.atomic():
                validated_data["parent_id"] = validated_data["parent"]
                del validated_data["parent"]

                validated_data["book_id"] = validated_data["book"]
                del validated_data["book"]

                instance.parent_id = validated_data["parent_id"]
                instance.book_id = validated_data["book_id"]
                instance.name = validated_data["name"]
                instance.slug = validated_data["slug"]
                instance.sub_name = validated_data["sub_name"]
                instance.save()
                return instance
        except Exception as e:
            raise CustomException(
                str(e),
                "could not update object",
                status_code=status.HTTP_424_FAILED_DEPENDENCY,
            )

    def create(self, validated_data: dict) -> Catalogue:
        try:
            with transaction.atomic():
                validated_data["book_id"] = validated_data["book"]
                del validated_data["book"]

                if self.parent_obj is not None:
                    validated_data["parent_id"] = self.parent_obj.id
                del validated_data["parent"]

                catalogue = Catalogue.objects.create(**validated_data)
                return catalogue
        except Exception as e:
            raise CustomException(
                str(e),
                "could not create object",
                status_code=status.HTTP_424_FAILED_DEPENDENCY,
            )

    def validate(self, attrs: dict):
        """
        This method is used to check for "page_number" in "attrs" (in other words, validated_data).
        """

        if (self.b.view_type == Book.STANDARD) and (attrs.get("start_page") is None):
            raise CustomException(
                "در کتاب استاندارد، شماره صفحه‌ی آغازین برای کاتالوگ اجاری است",
                "start_page",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        elif (self.b.view_type == Book.DEDICATED) and (
            attrs.get("start_page") is not None
        ):
            del attrs["start_page"]

        return super(WriteCatalogueSerializer, self).validate(attrs)

    def validate_parent(self, value):
        if value is not None:
            try:
                value = int(value)
                if value < 0:
                    raise ValueError()
            except ValueError:
                raise serializers.ValidationError("آی‌دی پدر، باید عددی نامنفی باشد")

            self.parent_obj = Catalogue.objects.filter(
                deleted_at=None, id=value
            ).first()
            if self.parent_obj is None:
                raise serializers.ValidationError("ترجمه کاتالوگ یافت نشد")

            if self.instance is not None:
                if (
                    self.instance.get_family()
                    .filter(deleted_at=None, id=value)
                    .exists()
                ):
                    raise serializers.ValidationError(
                        "پدر، نمیتواند از فرزندان یک فصل انتخاب شود"
                    )

        return value

    def validate_book(self, value):
        try:
            value = int(value)
            if value <= 0:
                raise ValueError()
        except ValueError:
            raise serializers.ValidationError("باید عددی مثبت باشد")

        self.b = Book.objects.filter(deleted_at=None, id=value).first()
        if self.b is None:
            raise serializers.ValidationError("کتاب یافت نشد")

        return value

    def validate_start_page(self, value):
        if value is not None:
            try:
                value = int(value)
                if value < 0:
                    raise ValueError()
            except ValueError:
                raise serializers.ValidationError(
                    "شماره صفحه‌ی آغازین فصل، باید عددی نامنفی باشد"
                )

        return value
