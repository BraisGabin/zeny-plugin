from django.db import models


class StorageManager(models.Manager):
    def get_queryset(self):
        return super(StorageManager, self).get_queryset().filter(bound='0', expire_time='0',).exclude(identify='0')
