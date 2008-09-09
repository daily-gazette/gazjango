from django.db                   import models
from django.contrib.contenttypes import generic
from accounts.models import UserProfile
from comments.models import PublicComment
from stories         import Article
from media.models    import ImageFile
from datetime import datetime

class PhotoSpread(Article):
    "A photo spread, which has a bunch of pages with one photo per page."
    photos = models.ManyToManyField(ImageFile, through='PhotoInSpread', related_name='spreads')
    
    def get_photo_number(self, num):
        try:
            return self.pages.get(number=num)
        except PhotoInSpread.DoesNotExist:
            return None
    
    def add_photo(self, photo, caption='', number=None):
        """
        Adds the given photo to this spread.
        
        If number is passed, rearrange other numbers so that this one
        lands as that number (like python's insert() for lists). Note that
        in this case we trash prior actual number attributes and preserve 
        only the relative ordering. Otherwise, put it at the end.
        """
        obj = PhotoInSpread(spread=self, photo=photo, caption=caption)
        pages = list(self.pages.order_by('number'))
        
        if number:
            pages.insert(number-1, obj)
        else:
            pages.append(obj)
        
        for i in range(len(pages)):
            page = pages[i]
            if page.number != i + 1:
                page.number = i + 1
                page.save() # this should always save the new photo
        
        return obj
    
    class Meta:
        app_label = 'articles'
    


class PhotoInSpread(models.Model):
    """
    One photo's being in a spread.
    
    Note we don't use order_with_respect_to because we want explicit access
    to the number for each photo, for use in URLs and such.
    """
    spread = models.ForeignKey(PhotoSpread, related_name="pages")
    photo  = models.ForeignKey(ImageFile, related_name="spread_pages")
    
    caption = models.TextField(blank=True)
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
        unique_together = (
            ('spread', 'photo'),
            ('spread', 'number')
        )
        ordering = ['spread', 'number']
        app_label = 'articles'
    
    def __unicode__(self):
        return "%s (in %s)" % (self.photo.slug, self.spread.slug)
    
    @models.permalink
    def get_absolute_url(self):
        return ('articles.views.spread', [self.slug, self.number])
    
