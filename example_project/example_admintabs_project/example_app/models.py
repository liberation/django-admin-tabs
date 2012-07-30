from django.db import models
from django.contrib.auth.models import User

class Article(models.Model):
    title = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255)
    content = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    is_online = models.BooleanField(default=False)

    categories = models.ManyToManyField('Category', blank=True)
    authors = models.ManyToManyField(User, blank=True)

    def __unicode__(self):
        return self.title

class Category(models.Model):
    title = models.CharField(max_length=255)

    def __unicode__(self):
        return self.title