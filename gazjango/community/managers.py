from django.db import models

import datetime
from operator import attrgetter

class EntryManager(models.Manager):
    def get_of_type_for_user(self, types, usernames):
        "Get entries of type `types` from the users `usernames`."
        return self.get_for_user(usernames, base=self.get_of_type(types))
    
    def get_of_type(self, types, base=None):
        """
        If `types` is a list/tuple, return entries of any of those types; otherwise, return
        entries of type `types`, or all of them if `types` is the special value "entries".
        
        Use `base` as the optional base for filtering.
        """
        if not base:
            base = self.all()
        
        if types == "entries":
            return base
        elif isinstance(types, (list, tuple,)):
            return base.filter(source_type__in=types)
        else:
            return base.filter(source_type=types)
    
    def get_for_user(self, usernames, base=None):
        "Get entries from the username or list of usernames `usernames`."
        if not base:
            base = self.all()
        
        if isinstance(usernames, (list, tuple)):
            return base.filter(owner_user__in=usernames)
        elif isinstance(usernames, basestring):
            return base.filter(owner_user=usernames)
        else:
            return base
    

class PublishedEntryManager(EntryManager):
    "A custom manager for entries, returning only published articles."
    
    def get_query_set(self):
        orig = super(PublishedEntryManager, self).get_query_set()
        return orig.filter(status__gte=2, timestamp__lte=datetime.datetime.now())
    
    def get_entries(self, base=None, num=None, **kwargs):
        '''Gets recent entries of various types.

        get_entries(num=5) will give you the 5 most recent entries of any type.

        get_entries(num=10, tweet=5) will give you 10 recent entries, no more
        than 5 of which will be tweets.

        get_entries(num=10, tweet=5, flickrphoto=5, bookmark=5) will give you
        10 recent entries, with no more than 5 each of tweets, flickr photos,
        or bookmarks.

        get_entries(tweet=3, flickrphoto=2, others=2) will give you the
        three most recent tweets, the two most recent photos from flickr, and
        the two most recent from other sources.

        get_entries(num=5, tweet=5, flickrphoto=5, others=0) will give you the
        5 most recent entries which are either tweets or flickrphotos.
        '''
        base = (base or self).order_by('-timestamp')
        entries = []

        sum_kwargs = sum(kwargs.itervalues())
        if num is None:
            if not kwargs:
                return []
            else:
                num = sum_kwargs

        for kind, kind_num in kwargs.iteritems():
            if kind != 'others':
                entries.extend(base.filter(source_type=kind)[:kind_num])

        if ('others' in kwargs) or (not kwargs) or (sum_kwargs < num):
            if kwargs.get('others', -1) != 0:
                exc_types = [k for k in kwargs.keys() if k != 'others']
                entries.extend(base.exclude(source_type__in=exc_types)[:num])

        # this is actually faster than heapq.nlargest for numbers we deal with
        return sorted(entries, key=attrgetter('timestamp'), reverse=True)[:num]
    

    def get_photos(self, base=None, num=3):
        base = (base or self).order_by('-timestamp')
        return base.filter(source_type='flickrphoto')[:num]
    
    def get_tweets(self, base=None, num=3):
        base = (base or self).order_by('-timestamp')
        return base.filter(source_type='tweet')[:num]


class TweetsManager(PublishedEntryManager):
    "A manager for tweets only."
    
    def get_query_set(self):
        orig = super(TweetsManager, self).get_query_set()
        return orig.filter(source_type='tweet')
