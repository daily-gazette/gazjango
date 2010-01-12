from django.db import models

import datetime

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
    
    def get_entries(self, base=None, num=10, exclusion=None, category=None):
        entries = (base or self).order_by('-timestamp')
        if category:
            entries = entries.filter(source_type=category)
        if exclusion:
            entries = entries.exclude(source_type=exclusion)
        return list(entries[:num])
    
    def get_photos(self, base=None, num=3):
        return list((base or self).order_by('-timestamp').filter(source_type="flickrphoto")[:num])
    
    def get_tweets(self, base=None, num=3):
        return list((base or self).order_by('-timestamp').filter(source_type="tweet")[:num])

class TweetsManager(PublishedEntryManager):
    "A manager for tweets only."
    
    def get_query_set(self):
        orig = super(TweetsManager, self).get_query_set()
        return orig.filter(source_type='tweet')
