from django.db import models
from django.contrib.auth.models import User
from articles.models import Article

class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True)
    articles = models.ManyToManyField(Article, related_name="authors")
