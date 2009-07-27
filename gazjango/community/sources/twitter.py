
from django.db import models
from django.contrib import admin
from django.utils.encoding import smart_unicode
from gazjango.community.sources import utils
from gazjango.community.models import Entry
from django.template import Template
import logging
import re

log = logging.getLogger('community.sources.twitter')

# model definition
class Tweet(Entry):
    tweet_id    = models.DecimalField(max_digits=20,decimal_places=0,null=True, blank=True, help_text="This is the id assigned to each tweet by twitter.")
    source      = models.TextField(blank=True, null=True, )
    icon        = models.CharField(max_length="200",blank=True)

    class Meta:
        ordering = ['-tweet_id',]
        app_label = "community"

    def __repr__(self):
        return "<Tweet id:%s>" % self.tweet_id

    def __unicode__(self):
        return u"Tweet: %s" % self.text

    # Here are a couple of properties to keep this backwards-compatible.
    @property
    def tweeter(self):
        return self.owner_user

    @property
    def text(self):
        return self.title

# admin definition (newforms admin only)
class TweetAdmin(admin.ModelAdmin):
    list_display = ('tweet_id', 'text', 'tweeter', 'timestamp',)

# retrieve function, this is how we handle items
def retrieve(force, **args):
    """ this is how we will create new items/tweets """
    username, password = args['account'], None
    if isinstance(username, tuple):
        username, password = username

    search = True
    user = False
    force = False
    search_term = "swarthmore"
    
    if search:
        print "[community.sources.twitter | INFO]: Working with Search"
        url = "http://search.twitter.com/search.json?q=%s" % search_term
        last_id = 0

        if force:
            log.info("Forcing update of all tweets available.")
        else:
            try:
                last_id = Tweet.objects.order_by('-tweet_id')[0].tweet_id
            except Exception, e:
                log.debug('%s', e)
        log.debug("Last id processed: %s", last_id)

        tweets = utils.get_remote_data(url, rformat="json")

        if not tweets:
            log.warning('no tweets returned, twitter possibly overloaded.')
            return
            
        tweets = tweets['results']
        for t in tweets:
            curr_id = t['id']
            if curr_id > last_id:
                log.info("Working with %s.", t['id'])

                tweet_text = t['text']
                tweet_text = re.sub(r'@((?:\w|\.(?=\w))+)',r'<a href="http://www.twitter.com/\1/">\1</a>',tweet_text)
                tweet_text = tweet_text.replace("@","&#64;")
                owner_user = smart_unicode(t['from_user'])
                url = "http://twitter.com/%s/statuses/%s" % (owner_user, t['id'])
                icon = t['profile_image_url'].replace("_normal","_bigger",1)
            
                tweet, created = Tweet.objects.get_or_create(
                        title       = str(curr_id) + " " + tweet_text[:50],
                        description = tweet_text,
                        tweet_id    = curr_id, 
                        timestamp   = utils.parsedate(t['created_at']),
                        source_type = "tweet",
                        owner_user  = owner_user,
                        url         = url,
                        icon        = icon,
                )
            
                tweet.source      = smart_unicode(t['source'])
            
            else:
                log.warning("No more tweets, stopping...")
                break        
    
    print "[community.sources.twitter | INFO]: Working with Users"
    url = "http://twitter.com/statuses/user_timeline/%s.json" % username
    last_id = 0

    if force:
        log.info("Forcing update of all tweets available.")
    else:
        try:
            last_id = Tweet.objects.filter(owner_user=username).order_by('-tweet_id')[0].tweet_id
        except Exception, e:
            log.debug('%s', e)
    log.debug("Last id processed: %s", last_id)

    if not password:
        tweets = utils.get_remote_data(url, rformat="json", username=username)
    else:
        tweets = utils.get_remote_data(url, rformat="json", username=username, password=password)

    if not tweets:
        log.warning('no tweets returned, twitter possibly overloaded.')
        return

    for t in tweets:
        if t['id'] > last_id:
            log.info("Working with %s.", t['id'])
            
            tweet_text = t['text']
            tweet_text = re.sub(r'@((?:\w|\.(?=\w))+)',r'<a href="http://www.twitter.com/\1/">\1</a>',tweet_text)
            tweet_text = tweet_text.replace("@","&#64;")
            owner_user = smart_unicode(t['user']['screen_name'])
            url = "http://twitter.com/%s/statuses/%s" % (owner_user, t['id'])
            icon = t['user']['profile_image_url'].replace("_normal","bigger",1)
        
            tweet, created = Tweet.objects.get_or_create(
                    title       = str(curr_id) + " " + tweet_text[:50],
                    description = tweet_text,
                    tweet_id    = curr_id, 
                    timestamp   = utils.parsedate(t['created_at']),
                    source_type = "tweet",
                    owner_user  = owner_user,
                    url         = url,
                    icon        = icon,
            )
        
            tweet.source      = smart_unicode(t['source'])
    
        else:
            log.warning("No more tweets, stopping...")
            break

admin.site.register(Tweet, TweetAdmin)
