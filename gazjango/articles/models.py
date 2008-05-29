from django.db                  import models
from django.contrib.auth.models import User
from accounts.models            import UserProfile
from datetime                   import datetime


class Article(models.Model):
    """A story or other article to be published.
    
    Includes news stories, editorials, etc, but not announcements or jobs."""
    
    # TODO: revisions, media, polls
    
    headline = models.CharField(max_length=250)
    subtitle = models.CharField(blank=True, max_length=200)
    slug     = models.SlugField(prepopulate_from=("headline",))
    
    summary  = models.TextField()
    text     = models.TextField()
    
    pub_date = models.DateTimeField(default=datetime.now)
    authors  = models.ManyToManyField(UserProfile, related_name="articles")
    category = models.ForeignKey('Category')
    
    def allow_edit(self, user):
        return self.authors.filter(user__username=user.username).count() > 0 \
            or user.has_perm('articles.change_article');
                              
    def __unicode__(self):
        return self.slug


class Category(models.Model):
    """A category of stories: news, features, etc.
    
    Only applies to Articles: Announcements don't use this."""
    
    name        = models.CharField(max_length=40)
    description = models.CharField(blank=True, max_length=250)
    slug        = models.SlugField(prepopulate_from=("name",))
    
    def __unicode__(self):
        return self.name


class Announcement(models.Model):
    """An announcement.
    
    The first day it runs is date_start, and the last is date_end."""
    
    slug       = models.SlugField()
    kind       = models.ForeignKey('AnnouncementKind')
    text       = models.TextField()
    date_start = models.DateField(default=datetime.today)
    date_end   = models.DateField(default=datetime.today)

    def __unicode__(self):
        return self.slug
    

class AnnouncementKind(models.Model):
    """ A kind of announcement: from the staff, the community, etc."""

    name = models.CharField(max_length=30)
    description = models.CharField(blank=True, max_length=250)

    def __unicode__(self):
        return self.name
