from django.db                         import models
from django.contrib.auth.models        import User
from accounts.models                   import UserProfile
from datetime                          import datetime, date
from diff_match_patch.diff_match_patch import diff_match_patch

class Article(models.Model):
    """A story or other article to be published.
    
    Includes news stories, editorials, etc, but not announcements or jobs."""
    
    headline = models.CharField(max_length=250)
    subtitle = models.CharField(blank=True, max_length=200)
    slug     = models.SlugField(prepopulate_from=("headline",), unique_for_date=True)
    
    summary  = models.TextField()
    text     = models.TextField()
    
    pub_date = models.DateTimeField(default=datetime.now)
    authors  = models.ManyToManyField(UserProfile, related_name="articles")
    category = models.ForeignKey('Category')
    
    def allow_edit(self, user):
        return self.authors.filter(user__pk=user.pk).count() > 0 \
            or user.has_perm('articles.change_article');
    
    def text_with_revisions(self):
        d = diff_match_patch()
        revised_text = self.text
        for r in self.revisions.filter(active=True):
            revised_text = d.patch_apply(d.patch_fromText(r.delta),revised_text)[0]
        return revised_text
    
    def revise_article(self, revised_text):
        d = diff_match_patch()
        revision = ArticleRevision()
        revision.article = self
        revision.delta = d.patch_toText(d.patch_make(self.text, revised_text))
        revision.save()
    
    def __unicode__(self):
        return self.slug
    

class ArticleRevision(models.Model):
    """ A revision of an article. Only deltas are stored."""
    
    article       = models.ForeignKey('Article', related_name='revisions')
    delta         = models.TextField()
    revision_date = models.DateTimeField(default=datetime.now)
    active        = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-revision_date']
    

class Category(models.Model):
    """A category of stories: news, features, etc.
    
    Only applies to Articles: Announcements don't use this."""
    
    name        = models.CharField(max_length=40, unique=True)
    description = models.CharField(blank=True, max_length=250)
    slug        = models.SlugField(prepopulate_from=("name",), unique=True)
    parent      = models.ForeignKey('self', blank=True, null=True,
                                    related_name='child_set')
    
    def __unicode__(self):
        return self.name
    

class Announcement(models.Model):
    """An announcement.
    
    The first day it runs is date_start, and the last is date_end."""
    
    slug       = models.SlugField(unique_for_month=True)
    kind       = models.ForeignKey('AnnouncementKind')
    text       = models.TextField()
    date_start = models.DateField(default=date.today)
    date_end   = models.DateField(default=date.today)
    
    def __unicode__(self):
        return self.slug


class AnnouncementKind(models.Model):
    """ A kind of announcement: from the staff, the community, etc."""
    
    name = models.CharField(max_length=30, unique=True)
    description = models.CharField(blank=True, max_length=250)
    
    def __unicode__(self):
        return self.name
    
