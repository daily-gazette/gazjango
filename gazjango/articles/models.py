from django.db import models
from django.contrib.auth.models import User

class Article(models.Model):
    """TODO: Expand this class. Right now, serves to demonstrate permissions system"""
    headline = models.CharField(max_length=250)
    text = models.TextField()
    
    def allow_edit(self, user):
        return self.authors.filter(user__username=user.username).count() > 0 or \
               user.has_perm('articles.change_article');

