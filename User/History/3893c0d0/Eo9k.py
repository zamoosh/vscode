from django.db import models


# FIXME: WHEN DELETE, name MUST BE PLACEHOLDER
class Lang(models.Model):
    name = models.CharField(max_length=50, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True)

    def __str__(self):
        return self.name

    def delete(self, using=None, keep_parents=False) -> None:
        raise Exception("delete is not implemented yet!")
