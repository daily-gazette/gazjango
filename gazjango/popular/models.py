import datetime

from django.contrib.contenttypes        import generic
from django.contrib.contenttypes.models import ContentType
from django.db                          import models

from gazjango.articles.models.stories import Article

# Create your models here.

class StoryRank(models.Model):
    """
    A foreign key to a story and the number of hits it has. Only created when a story receives any views.
    """
    
   
    hits        = models.IntegerField(max_length=7)
    last_update = models.DateTimeField(blank=False)
    article     = models.ForeignKey(Article)
    