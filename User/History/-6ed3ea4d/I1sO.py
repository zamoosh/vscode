from django.db import models
from django.contrib.postgres.fields import ArrayField


class Command(models.Model):
    COMMAND = 0

    TYPE_CHOICES = ()

    parent = models.ForeignKey("self", null=True, on_delete=models.SET_NULL)
    type = models.PositiveSmallIntegerField(default=0)

    model_ids = ArrayField(models.PositiveIntegerField)
    required = models.BooleanField(default=False)
    description = models.TextField(null=True)
    icon = models.CharField(max_length=500)

    command = models.TextField(null=True)
    sms_command = models.TextField(null=True)

    password = models.CharField(max_length=255)
    password_title = models.CharField(max_length=255)
