from django.db import models
from django.utils import timezone

from datetime import timedelta


class UserQuery(models.Model):
    qid = models.AutoField(primary_key=True)
    query = models.CharField(max_length=250)
    created_date = models.DateTimeField(auto_now_add=True)

    def is_expired(self) -> bool:
        return timezone.now() > self.created_date + timedelta(hours=3)

    def __str__(self) -> str:
        return self.query


class Result(models.Model):
    rid = models.AutoField(primary_key=True)
    qid = models.ForeignKey(to=UserQuery, on_delete=models.CASCADE)
    search_engine = models.CharField(max_length=32)
    title = models.CharField(max_length=128)
    description = models.TextField()
    link = models.CharField(max_length=64)

    def __str__(self) -> str:
        return self.title
