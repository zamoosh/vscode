from django.db import models
from language.models import Lang


class Book(models.Model):
    lang = models.ForeignKey(Lang, on_delete=models.CASCADE)

    title = models.CharField(max_length=255)
    subject = models.CharField(max_length=255)
    writer = models.CharField(max_length=255)
    editor = models.CharField(max_length=255, null=True)
    standard_number = models.CharField(max_length=255, null=True)
    publisher = models.CharField(max_length=255)
    publish_date = models.DateTimeField(null=True)
    cover_count = models.PositiveIntegerField()
    cover_number = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

    def delete(self, using=None, keep_parents=False) -> None:
        raise Exception("delete is not implemented yet!")
