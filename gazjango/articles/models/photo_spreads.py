from django.db                   import models
from django.contrib.contenttypes import generic
from gazjango.accounts.models         import UserProfile
from gazjango.comments.models         import PublicComment
from gazjango.articles.models.stories import Article
from gazjango.media.models            import ImageFile
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
    
    N.B. that ordering will only work if numbers are sequential. (This is
    because it should always be that way, and allowing them not to be is
    somewhat slower.) If you build up the photospread with add_photo, ordering
    is guaranteed to work.
    
    Note we don't use order_with_respect_to because we want explicit access
    to the number for each photo, for use in URLs and such.
    """
    spread = models.ForeignKey(PhotoSpread, related_name="pages")
    photo  = models.ForeignKey(ImageFile, related_name="spread_pages")
    
    caption = models.TextField(blank=True)
    number  = models.PositiveIntegerField()
    
    def next(self):
        try:
            return self.spread.pages.get(number=self.number+1)
        except PhotoInSpread.DoesNotExist:
            return None
    
    def prev(self):
        try:
            return self.spread.pages.get(number=self.number-1)
        except PhotoInSpread.DoesNotExist:
            return None
    
    def has_next(self):
        return bool(self.spread.pages.filter(number=self.number + 1))
    
    def has_prev(self):
        return bool(self.spread.pages.filter(number=self.number - 1))
    
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
        a = self.spread
        d = a.pub_date
        return ('photospread', [d.year, d.month, d.day, a.slug, self.number])
    
