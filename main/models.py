from django.db import models
from manticore.models import fields, SearchIndex


class XxxHub(SearchIndex):
    title = fields.RTField()
    date = models.DateTimeField(auto_now_add=True)
    image = models.CharField(max_length=5000, default='')
    thumb = models.CharField(max_length=5000, default='')
    cse = models.JSONField(blank=True)
    status = models.IntegerField(default=0)


class Content(models.Model):
    title = models.CharField(max_length=2500, db_index=True, unique=True)
    date = models.DateTimeField(default='CURRENT_TIMESTAMP')
    image = models.TextField(null=True, blank=True)
    thumb = models.TextField(null=True, blank=True)
    cse = models.JSONField(null=True, blank=True)
    status = models.IntegerField(default=0)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.title
