from django.db import models
from django.contrib.contenttypes.models import ContentType

class TagGroup(models.Model):
    """
    A category of tags. Applies only to a certain content type.
    
    If the group has no name, it represents the "miscellaneous" category.
    """
    name = models.CharField(max_length=60, unique=True)
    content_types = models.ManyToManyField(ContentType)
    
    active_tags = property(lambda self: self.tags.filter(is_active=True))
    
    def __unicode__(self):
        return self.name
    

class Tag(models.Model):
    "A tag."
    name = models.CharField(max_length=50, db_index=True)
    verbose_name = models.CharField(max_length=80, blank=True)
    is_active = models.BooleanField(default=True, blank=True)
    group = models.ForeignKey(TagGroup, related_name="tags")
    
    def longest_name(self):
        return self.verbose_name or self.name
    
    class Meta:
        ordering = ('name',)
        unique_together = ('name', 'group')
    
    def __unicode__(self):
        return self.name
    
