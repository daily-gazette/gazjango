from django.core.cache import cache
from django.db         import models
from gazjango.scrapers import feedparser

FEED_TIMEOUT = 2*60*60 + 10*60

class OutsideSiteManager(models.Manager):
    def most_recent_stories(self):
        return sorted( (site.feed.entries[0] for site in self.all()),
                       key=lambda entry: entry.date,
                       reverse=True)

class OutsideSite(models.Model):
    name = models.CharField(max_length=100)
    feed_url = models.URLField(verify_exists=True)
    link = models.URLField(blank=True, verify_exists=True)
    
    TYPE_CHOICES = [
        ('g', 'Group site'),
        ('n', 'News'),
        ('b', 'Blog'),
    ]
    type = models.CharField(max_length=1, choices=TYPE_CHOICES)
    
    objects = OutsideSiteManager()
    
    def _cache_key(self):
        return "parsed-feed-%s" % self.pk
    
    def _get_feed(self):
        key = self._cache_key()
        cached = cache.get(key, None)
        if cached:
            return cached
        new = feedparser.parse(self.feed_url)
        cache.set(key, new, FEED_TIMEOUT)
        return new
    feed = property(_get_feed)
    
    def __unicode__(self):
        return self.name
    

def clear_cached_feed(sender, instance, **kwargs):
    cache.delete(instance._cache_key())
models.signals.post_save.connect(clear_cached_feed, sender=OutsideSite)
