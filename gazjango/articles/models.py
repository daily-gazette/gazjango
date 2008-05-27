from django.db                  import models
from django.contrib.auth.models import User
from accounts.models            import UserProfile
import datetime


class Article(models.Model):
    """A story or other article to be published.
    
    Includes news stories, editorials, etc, but not announcements or jobs."""
    
    # TODO: revisions, media, polls
    
    headline = models.CharField(max_length=250)
    subtitle = models.CharField(blank=True, max_length=200)
    slug     = models.SlugField(prepopulate_from=("headline",))
    
    summary  = models.TextField()
    text     = models.TextField()
    
    pub_date = models.DateTimeField(default=datetime.datetime.now)
    authors  = models.ManyToManyField(UserProfile, related_name="articles")
    category = models.ForeignKey('Category')
    
    def allow_edit(self, user):
        return self.authors.filter(user__username=user.username).count() > 0 or \
               user.has_perm('articles.change_article');
                              
    def __unicode__(self):
        return slug


class Category(models.Model):
    """A category of stories: news, features, etc.
    
    Only applies to Articles: Announcements don't use this."""
    
    name        = models.CharField(max_length=40)
    description = models.CharField(blank=True, max_length=250)
    slug        = models.SlugField(prepopulate_from=("name",))
    
    def __unicode__(self):
        return u"Category"


class Announcements(models.Model):
    """An announcement: either a staff announcement or a community one.
    
    The first day it runs is date_start, and the last is date_end."""
    
    slug       = models.SlugField()
    kind       = models.CharField(max_length=30)
    text       = models.TextField()
    date_start = models.DateField(default=datetime.datetime.today)
    date_end   = models.DateField(default=datetime.datetime.today)

    def __unicode__(self):
        return slug
