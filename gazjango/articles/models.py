from django.db                         import models
from django.contrib.auth.models        import User
from accounts.models                   import UserProfile
from exceptions                        import RelationshipMismatch
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
    
    def text_at_revision(self, revision):
        """Returns the text as it was at the specified revision."""
        if revision.article != self:
            raise RelationshipMismatch()
        d = diff_match_patch()
        rewound = self.text
        for r in self.revisions.filter(active=True, date__gte=revision.date):
            rewound = d.patch_apply(d.patch_fromText(r.delta), rewound)[0]
        return rewound
    
    def revise_text(self, revised_text):
        d = diff_match_patch()
        patch = d.patch_toText(d.patch_make(revised_text, self.text))
        revision = ArticleRevision.objects.create(article=self, delta=patch)
        
        self.text = revised_text
        self.save()
    
    def __unicode__(self):
        return self.slug
    

class ArticleRevision(models.Model):
    """ A revision of an article. Only deltas are stored.
    
    Note that the most recent text is stored in the article's text attribute, while 
    earlier versions are stored as revisions...as such, these are "reverse diffs."
    For example, if an article has versions 1, 2, and 3, version 3 is stored directly
    with the article, and there are ArticleRevisions to go from 3 to 2 and from 2 to
    1."""
    
    article = models.ForeignKey('Article', related_name='revisions')
    delta   = models.TextField()
    date    = models.DateTimeField(default=datetime.now)
    active  = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-date']
    
    def __unicode__(self):
        return u"%s - %s" % (self.article.slug, self.date)
    

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
    
