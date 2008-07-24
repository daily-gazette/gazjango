from django.db             import models
from gazjango.media.models import ImageFile
from datetime              import datetime

class SpecialsCategory(models.Model):
    name = models.CharField(max_length=100)
    
    def __unicode__(self):
        return self.name
    
    class Meta:
        app_label = 'articles'
    

class Special(models.Model):
    "A special thing / article / whatever to be advertised on the homepage."
    
    title = models.CharField(max_length=100)
    category = models.ForeignKey(SpecialsCategory)
    date = models.DateTimeField(default=datetime.now)
    
    image = models.ForeignKey(ImageFile)
    url = models.URLField()
    
    def __unicode__(self):
        return self.title
    
    class Meta:
        app_label = 'articles'
    
