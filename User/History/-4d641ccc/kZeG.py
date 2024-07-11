from django.db import transaction
from rest_framework import serializers
from rest_framework import status
from ...models import Lang
from library.drf_exception import CustomException
from colorful_logging import c_print


class ReadLangSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lang
        fields = ["id", "name"]


class WriteLangSerializer(serializers.Serializer):
    name = serializers.CharField(trim_whitespace=True)

    def update(self, instance: Lang, validated_data):
        try:
            with transaction.atomic():
                instance.name = validated_data['name']
                instance.save()
                return instance
        except Exception as e:
            raise CustomException(str(e), "could not update object", status_code=status.HTTP_424_FAILED_DEPENDENCY)

    def create(self, validated_data):
        try:
            with transaction.atomic():
                lang = Lang.objects.create(**validated_data)
                return lang
        except Exception as e:
            raise CustomException(str(e), "could not create object", status_code=status.HTTP_424_FAILED_DEPENDENCY)

    def validate_name(self, value: str):
        value = value.strip()
        if Lang.objects.filter(deleted_at=None, name=value).exists():
            raise serializers.ValidationError("این نام از قبل انتخاب شده است")

        return value
