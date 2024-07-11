from django.db import models


class Book(models.Model):
    lang = models.ForeignKey(Lang, on_delete=models.CASCADE)

    title = models.CharField(max_length=255)
    subject = models.CharField(max_length=255)
    writer = models.CharField(max_length=255)
    editor = models.CharField(max_length=255, null=True)
    standard_number = models.CharField(max_length=255, null=True)
    publisher = models.CharField(max_length=255)
    publish_date = models.DateTimeField(null=True)
    page_count = models.PositiveIntegerField()
    cover_count = models.PositiveIntegerField()
    cover_number = models.PositiveIntegerField()
    view_type = models.PositiveSmallIntegerField(
        default=DEDICATED, choices=VIEW_TYPE_CHOICES
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

    def delete(self, using=None, keep_parents=False):
        raise Exception("delete is not implemented yet!")
