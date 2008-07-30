from diff_match_patch.diff_match_patch import diff_match_patch
from datetime import datetime
from scrapers.BeautifulSoup import BeautifulSoup
import re

from django.db                   import models
from django.contrib.auth.models  import User
from django.contrib.contenttypes import generic

from accounts.models            import UserProfile
from comments.models            import PublicComment
from media.models               import MediaFile, ImageFile, MediaBucket
from articles.exceptions        import RelationshipMismatch
import articles.formats as formats


class PublishedArticlesManager(models.Manager):
    "A custom manager for Articles, returning only published articles."
    def get_query_set(self):
        orig = super(PublishedArticlesManager, self).get_query_set()
        return orig.filter(status='p')
    
    def get_top_story(self):
        """Returns a random published article with position=1.
        
        There should generally only be one, but just in case, we rotate."""
        return self.filter(position=1).order_by("?")[0]
    
    def get_secondary_stories(self, num=2):
        """Returns a list of ``num`` stories with position=2."""
        return self.filter(position=2).order_by("-pub_date")[:num]
    
    def get_tertiary_stories(self, num=6):
        """Returns the ``num`` most recent stories with a null position."""
        return self.filter(position=None).order_by("-pub_date")[:num]
    


class Article(models.Model):
    """
    A story or other article to be published. Includes news stories,
    editorials, etc, but not announcements or jobs.
    
    Note that although there are a ton of summaries, only major stories (ie
    thoe that go in the topstories bit) need a long_summary or a short_summary.
    All stories, however, should have a regular summary.
    
    Stores major revisions of the article: whatever the author decides to
    save manually while writing, changes editors make afterwards, and then
    any changes made after publication. Comments can (and should) be attached
    to these revisions.
    """
    
    headline    = models.CharField(max_length=200)
    short_title = models.CharField(blank=True, max_length=100)
    subtitle    = models.CharField(blank=True, max_length=200)
    slug        = models.SlugField(unique_for_date="pub_date")
    
    summary = models.TextField()
    short_summary = models.CharField(max_length=150)
    long_summary  = models.TextField(blank=True)
    
    text   = models.TextField()
    format = models.ForeignKey('Format')
    
    pub_date = models.DateTimeField(default=datetime.now)
    authors  = models.ManyToManyField(UserProfile, related_name="articles")
    category = models.ForeignKey('articles.Category')
    
    front_image = models.ForeignKey(ImageFile, null=True, related_name="articles_with_front")
    thumbnail   = models.ForeignKey(ImageFile, null=True, related_name="articles_with_thumbnail")
    media  = models.ManyToManyField(MediaFile, related_name="articles")
    bucket = models.ForeignKey(MediaBucket, null=True, related_name="articles")
    
    comments = generic.GenericRelation(PublicComment,
                                       content_type_field='subject_type',
                                       object_id_field='subject_id')
    
    STATUS_CHOICES = (
        ('d', 'Draft'),
        ('e', 'Pending Review'),
        ('w', 'Scheduled'),
        ('p', 'Published')
    )
    status = models.CharField(max_length=1, choices=STATUS_CHOICES)
    
    comments_allowed = models.BooleanField(default=True)
    
    position  = models.PositiveSmallIntegerField(blank=True, null=True)
    # null = nothing special, 1 = top story, 2 = second-tier story
    
    objects = models.Manager()
    published = PublishedArticlesManager()
    
    def get_title(self):
        return (self.short_title or self.headline)
    
    
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
    
    
    def formatted_text(self, revision=None):
        text = self.text_at_revision(revision) if revision else self.text
        formatter = getattr(formats, self.format.function)
        return formatter(text)
    
    
    def resolved_text(self, revision=None):
        """
        Formats the text (at the revision specified by ``revision``, if
        passed) and then goes through and replaces the image references within
        it to links that will actually work.
        """
        text = self.formatted_text(revision)
        if self.media.count() > 0 or re.search("<img", text, re.IGNORECASE):
            soup = BeautifulSoup(text)
            
            reg = re.compile(r"^\s*https?://")
            matches = lambda src: not re.match(reg, src)
            for image in soup.findAll("img", src=matches):
                image['src'] = self.resolve_image_link(image['src'])
            
            return unicode(soup)
        else:
            return text
    
    def resolve_image_link(self, image_path, complain=False):
        """
        Turns relative image links in articles into absolute URLs. For
        example, if an article's text includes "<img src='cool-pic'/>",
        ``resolved_text`` will call this function to replace 'cool-pic' with
        '/files/some-bucket/cool-pic'. This function will also add any 
        
        If the path in the image includes a '/', it's parsed as 
        'bucket-slug/image-slug'. Otherwise, we first check the media files
        that are explicitly associated with this article, and then this
        article's bucket. This can potentially cause confusion if the
        article is associated with 'lame-bucket', 'awesome-bucket/cool-pic'
        is in the article's media m2m, and 'lame-bucket' has a file called 
        'cool-pic'. In this case, we use 'awesome-bucket/cool-pic'.
        
        This function will throw a MediaFile.MultipleObjectsReturned
        error, or return "[ambiguous reference to (slug)]", depending on the
        value of ``complain``, if article.media has more than one file (in
        different buckets) with the same slug, and the bucket slug is not
        explicit. Don't let this happen. The UI for setting associated media
        should either not allow this, or give stern warnings.
        """
        if "/" in image_path:
            bucket_slug, slug = image_path.split("/", 1)
            args = {'bucket__slug': bucket_slug, 'slug': slug}
        else:
            args = {'slug': image_path}
        
        if complain:
            def error(exception, message): raise exception
        else:
            def error(exception, message): return message
        
        try: # self.media should be cached, so we try it first
            image = self.media.get(**args)
        except MediaFile.DoesNotExist:
            try:
                args.setdefault('bucket__slug', self.bucket.slug)
                image = ImageFile.objects.get(**args)
                self.media.add(image)
            except ImageFile.DoesNotExist, e:
                return error(e, "")
        except MediaFile.MultipleObjectsReturned, e:
            return error(e, "[ambiguous reference to '%s']" % image_path)
        
        return image.get_absolute_url()
    
    
    def related_list(self, num=None):
        """Returns a QuerySet of related stories."""
        # TODO: improve related_list
        related = self.category.root().all_articles()
        related = related.exclude(pk=self.pk).order_by('-pub_date')
        return related[:num] if num else related
    
    
    def __unicode__(self):
        return self.slug
    
    @models.permalink
    def get_absolute_url(self):
        d = self.pub_date
        a = [str(x) for x in (d.year, d.month, d.day)]
        return ('articles.views.article', a + [self.slug])
    
    class Meta:
        app_label = 'articles'
    


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
        app_label = 'articles'
    
    def __unicode__(self):
        return u"%s - %s" % (self.article.slug, self.date)
    

class Format(models.Model):
    """ A format: html, textile, etc. """
    
    name     = models.CharField(max_length=30, unique=True)
    function = models.CharField(max_length=30)
    
    def __unicode__(self):
        return self.name
    
    class Meta:
        app_label = 'articles'
    
