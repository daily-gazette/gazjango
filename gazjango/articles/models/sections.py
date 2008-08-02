from django.db import models

class Section(models.Model):
    """
    A section of coverage: news, features, opinions, columns....
    
    Each article belongs to exactly one section, and any number
    of subsections within that section.
    """
    
    name = models.CharField(max_length=40, unique=True)
    slug = models.SlugField(unique=True)
    description = models.CharField(max_length=250, blank=True)
    
    class Meta:
        app_label = 'articles'
    
    def __unicode__(self):
        return self.name
    
    @models.permalink
    def get_absolute_url(self):
        return ('section', [self.slug])
    

class Subsection(models.Model):
    """
    A subsection: Ask the Gazette, College News, a specific column, whatever.
    """
    
    name = models.CharField(max_length=40)
    slug = models.SlugField(unique=True)
    description = models.CharField(max_length=250, blank=True)
    section = models.ForeignKey(Section)
    
    class Meta:
        app_label = 'articles'
    
    def __unicode__(self):
        return self.name
    
    @models.permalink
    def get_absolute_url(self):
        return ('subsection', [self.section.slug, self.slug])
    
