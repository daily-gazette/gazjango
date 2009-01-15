from django.core.cache import cache
from django.db         import models
from gazjango.scrapers import feedparser

FEED_TIMEOUT = 2*60*60 + 10*60
BROKEN_FEED_TIMEOUT = 2*60

class OutsideSiteManager(models.Manager):
    def most_recent_stories(self, num_from_each=1, spec=models.Q()):
        """
        Return the `num_from_each` most recent stories from each OutsideSite
        specified by `spec` (defaults to all), sorted most recent first. The
        return format looks like
            [(<OutsideSite: Site1>, <Story1>), (<OutsideSite: Site2>, <Story2>)]
        with <Story1> being the object returned by feedparser.
        
        See http://feedparser.org for documentation on the returned objects.
        
        Note that this might be quite slow if the feeds aren't already
        up to date.
        """
        stories = []
        for site in self.filter(spec):
            if not site.feed.bozo:
                stories.extend(site.feed.entries[:num_from_each])
        return sorted(stories, key=lambda entry: entry.date, reverse=True)
    
    def update_all(self):
        "Forces a refresh of all feeds."
        for site in self.all():
            site.update_feed()
            

class OutsideSite(models.Model):
    """
    An outside site to be included in a blogroll-type thing.
    
    The feed attribute is the result of feedparser.parse: see 
    http://feedparser.org for more complete documentation. Note
    that it may be completely invalid, in which case its "bozo"
    attribute will be true.
    """
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
        return cached if cached else _update_feed()
    feed = property(_get_feed)
    
    def update_feed(self):
        new = feedparser.parse(self.feed_url)
        timeout = BROKEN_FEED_TIMEOUT if new.bozo else FEED_TIMEOUT
        cache.set(self._cache_key(), new, timeout)
        return new
    
    def __unicode__(self):
        return self.name
    

def reset_feed(sender, instance, **kwargs):
    instance.update_feed()
models.signals.post_save.connect(reset_feed, sender=OutsideSite)
