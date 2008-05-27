from django.db import models
from django.contrib.auth.models import User

class Article(models.Model):
    """TODO: Expand this class. Right now, serves to demonstrate permissions system"""
    headline = models.CharField(max_length=250)
    text = models.TextField()
    
    def allow_edit(self, user):
        if(user.get_profile() in self.authors.all() or user.has_perm('articles.change_article')):
            return True
        else:
            return False

