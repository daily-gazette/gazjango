from django.db                   import models
from django.contrib.contenttypes import generic
from accounts.models import UserProfile
from media.models    import ImageFile
from datetime import datetime

class PhotoSpread(models.Model):
    "A photo spread, which has a bunch of pages with one photo per page."
    title    = models.CharField(max_length=150)
    slug     = models.SlugField(unique_for_date="pub_date")
    creators = models.ManyToManyField(UserProfile)
    pub_date = models.DateTimeField(default=datetime.now)
    
    comments = generic.GenericRelation(PublicComment,
                                       content_type_field='subject_type',
                                       object_id_field='subject_id')
    
    def get_photo_number(self, num):
        try:
            self.pages.get(number=num)
        except PhotoInSpread.DoesNotExist:
            return None
    
    class Meta:
        app_label = 'articles'
    
    def __unicode__(self):
        return self.slug
    
    @models.permalink
    def get_absolute_url(self):
        return ('articles.views.spread', [self.slug])
    

class PhotoInSpread(models.Model):
    """
    One photo's being in a spread.
    
    Note we don't use order_with_respect_to because we want explicit access
    to the number for each photo, for use in URLs and such.
    """
    spread = models.ForeignKey(PhotoSpread, related_name="pages")
    photo  = models.ForeignKey(ImageFile, related_name="spread_pages")
    
    caption = models.TextField()
    number  = models.PositiveIntegerField()
    
    def next(self):
        try:
            great = self.objects.filter(spread=spread, number__gte=self.number)
            return great.order_by('number')[0]
        except IndexError:
            return None
    
    def prev(self):
        try:
            less = self.objects.filter(spread=spread, number__lte=self.number)
            return less.order_by("-number")[0]
        except IndexError:
            return None
    
    class Meta:
        unique_together = ('photo', 'spread')
        ordering = ['spread', 'number']
        app_label = 'articles'
    
    def __unicode__(self):
        return "%s (in %s)" % (self.photo.slug, self.spread.slug)
    
    @models.permalink
    def get_absolute_url(self):
        return ('articles.views.spread', [self.slug, self.number])
    
