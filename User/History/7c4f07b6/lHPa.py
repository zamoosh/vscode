from django.db import transaction
from rest_framework import serializers
from rest_framework import status
from book.models import Book, Lang
from library.drf_exception import CustomException
from .lang_serializer import ReadLangSerializer
from .catalogue_serializer import ReadCatalogueIdNameSerializer


class ReadBookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = [
            "lang",
            "id",
            "title",
            "subject",
            "writer",
            "editor",
            "standard_number",
            "publisher",
            "publish_date",
            "cover_count",
            "cover_number",
            "page_count",
            "catalogue_count",
        ]

    # catalogue_set = serializers.SerializerMethodField()
    catalogue_count = serializers.SerializerMethodField()
    lang = ReadLangSerializer()

    def get_view_type(self, obj: Book):
        res = {"value": obj.view_type}
        if obj.view_type == Book.STANDARD:
            res["name"] = "استاندارد"
        elif obj.view_type == Book.DEDICATED:
            res["name"] = "اختصاصی"

        return res

    def get_catalogue_set(self, obj: Book):
        return ReadCatalogueIdNameSerializer(obj.catalogue_set.all(), many=True).data

    def get_catalogue_count(self, obj: Book):
        return obj.catalogue_set.count()


class WriteBookSerializer(serializers.Serializer):
    title = serializers.CharField(trim_whitespace=True)
    subject = serializers.CharField(trim_whitespace=True)
    writer = serializers.CharField(trim_whitespace=True)
    editor = serializers.CharField(allow_null=True, trim_whitespace=True)
    lang = serializers.IntegerField()  # Lang's id
    standard_number = serializers.CharField(allow_null=True)
    publisher = serializers.CharField(trim_whitespace=True)
    publish_date = serializers.DateTimeField()
    page_count = serializers.IntegerField()
    cover_count = serializers.IntegerField()
    cover_number = serializers.IntegerField()

    def to_representation(self, instance):
        return ReadBookSerializer(instance).data

    def update(self, instance: Book, validated_data):
        try:
            with transaction.atomic():
                instance.title = validated_data["title"]
                instance.subject = validated_data["subject"]
                instance.writer = validated_data["writer"]
                instance.editor = validated_data["editor"]
                instance.lang_id = validated_data["lang"]
                instance.standard_number = validated_data["standard_number"]
                instance.publisher = validated_data["publisher"]
                instance.publish_date = validated_data["publish_date"]
                instance.page_count = validated_data["page_count"]
                instance.cover_count = validated_data["cover_count"]
                instance.cover_number = validated_data["cover_number"]
                instance.view_type = validated_data["view_type"]
                instance.save()
                return instance
        except Exception as e:
            raise CustomException(
                str(e),
                "could not create object",
                status_code=status.HTTP_424_FAILED_DEPENDENCY,
            )

    def create(self, validated_data) -> Book:
        try:
            with transaction.atomic():
                validated_data["lang_id"] = validated_data["lang"]
                del validated_data["lang"]

                book = Book.objects.create(**validated_data)
                return book
        except Exception as e:
            raise CustomException(
                str(e),
                "could not create object",
                status_code=status.HTTP_424_FAILED_DEPENDENCY,
            )

    def validate_lang(self, value):
        try:
            value = int(value)
        except ValueError:
            raise serializers.ValidationError("آی‌دی زبان باید عددی باشد")

        lang = Lang.objects.filter(deleted_at=None, id=value).first()
        if lang is None:
            raise serializers.ValidationError("زبان یافت نشد")

        return value

    def validate_page_count(self, value):
        try:
            value = int(value)
        except ValueError:
            raise serializers.ValidationError("تعداد صفحات باید عددی مثبت باشد")
        if value <= 0:
            raise serializers.ValidationError(
                "تعداد صفحات باید عددی بزرگتر از صفر باشد"
            )
        return value

    def validate_cover_count(self, value):
        try:
            value = int(value)
        except ValueError:
            raise serializers.ValidationError("تعداد جلد باید عددی مثبت باشد")
        if value <= 0:
            raise serializers.ValidationError("تعداد جلد باید عددی بزرگتر از صفر باشد")
        return value

    def validate_cover_number(self, value):
        try:
            value = int(value)
        except ValueError:
            raise serializers.ValidationError("شماره جلد باید عددی مثبت باشد")
        if value <= 0:
            raise serializers.ValidationError("شماره جلد باید عددی بزرگتر از صفر باشد")
        return value

    def validate_view_type(self, value):
        valid_choices: list[int] = list(
            map(lambda item: item[0], Book.VIEW_TYPE_CHOICES)
        )
        if not (value in valid_choices):
            raise serializers.ValidationError("نوع نمایش معتبر نیست")

        return value


class PageNumberSerializer(serializers.Serializer):
    page_number = serializers.IntegerField()
