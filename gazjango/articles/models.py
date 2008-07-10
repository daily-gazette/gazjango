from django.db                         import models
from django.db.models                  import permalink
from django.contrib.auth.models        import User
from accounts.models                   import UserProfile
from exceptions                        import RelationshipMismatch
from datetime                          import datetime, date
from diff_match_patch.diff_match_patch import diff_match_patch
import formats
import tagging

class Article(models.Model):
    """A story or other article to be published.
    
    Includes news stories, editorials, etc, but not announcements or jobs."""
    
    headline  = models.CharField(max_length=250)
    subtitle  = models.CharField(blank=True, max_length=200)
    slug      = models.SlugField(prepopulate_from=("headline",), unique_for_date="pub_date")
    
    summary   = models.TextField()
    text      = models.TextField()
    
    pub_date  = models.DateTimeField(default=datetime.now)
    authors   = models.ManyToManyField(UserProfile, related_name="articles")
    category  = models.ForeignKey('Category')
    
    published = models.BooleanField()
    format    = models.ForeignKey('Format')
    
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
    
    def formatted_text(self):
        formatter = getattr(formats, self.format.function)
        return formatter(self.text)
    
    def formatted_text_at_revision(self, revision):
        formatter = getattr(formats, self.format.function)
        return formatter(self.text_at_revision(revision))
    
    def __unicode__(self):
        return self.slug
    
    @permalink
    def get_absolute_url(self):
        d = self.pub_date
        a = [str(x) for x in (d.year, d.month, d.day)]
        return ('articles.views.article', a + [self.slug])
    

try:
    tagging.register(Article)
except tagging.AlreadyRegistered:
    pass # this happens in testing, for some reason


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
    
    Only applies to Articles: Announcements use AnnouncementKind."""
    
    name        = models.CharField(max_length=40, unique=True)
    description = models.CharField(blank=True, max_length=250)
    slug        = models.SlugField(prepopulate_from=("name",), unique=True)
    parent      = models.ForeignKey('self', blank=True, null=True,
                                    related_name='child_set')
    
    def ancestors(self):
        """Returns all super-categories of this category, including itself."""
        if self.parent is None:
            return [self]
        else:
            return self.parent.ancestors() + [self]
    
    def descendants(self):
        "Returns all sub-categories of this category, including itself."
        descendants = [self]
        for child in self.child_set.all():
            descendants.extend(child.descendants())
        return descendants
    
    def all_articles(self):
        "Returns all articles in this category or one of its sub-categories."
        Article.objects.filter(category__in=[d.pk for d in self.descendants()])
    
    def __unicode__(self):
        return self.name
    
    @permalink
    def get_absolute_url(self):
        return ('articles.views.category', [self.slug])
    

class Announcement(models.Model):
    """An announcement.
    
    The first day it runs is date_start, and the last is date_end."""
    
    slug       = models.SlugField(unique_for_month="date_start")
    kind       = models.ForeignKey('AnnouncementKind')
    text       = models.TextField()
    date_start = models.DateField(default=date.today)
    date_end   = models.DateField(default=date.today)
    
    # TODO: replace unique_for_month with a custom validator that checks the span
    
    def __unicode__(self):
        return self.slug
    
    @permalink
    def get_absolute_url(self):
        d = self.pub_date
        a = [str(x) for x in (d.year, d.month, d.day)]
        return ('articles.views.announcement', a + [self.slug])
    

class AnnouncementKind(models.Model):
    """ A kind of announcement: from the staff, the community, etc."""
    
    name = models.CharField(max_length=30, unique=True)
    description = models.CharField(blank=True, max_length=250)
    
    def __unicode__(self):
        return self.name
    
    @permalink
    def get_absolute_url(self):
        return ('articles.views.announcement_kind', [self.slug])
    

class Format(models.Model):
    """ A format: html, textile, etc. """
    
    name     = models.CharField(max_length=30, unique=True)
    function = models.CharField(max_length=30)

