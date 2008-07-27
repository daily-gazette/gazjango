from django.db                          import models
from django.utils.encoding              import smart_str
from django.contrib.sites.models        import Site
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes        import generic

from accounts.models import UserProfile

from datetime import datetime
import misc.akismet
import settings


class CommentsManager(models.Manager):
    def new(self, check_spam=True, **data):
        """
        Makes a new comment, checking it for spam if necessary -- that is,
        the user doesn't have the `comments.can_post_directly` permission,
        and `check_spam` is not set to False.
        """
        comment = PublicComment(**data)
        
        user = data.get('user', None)
        if user and user.has_perm('comments.can_post_directly'):
            comment.is_spam = False
            comment.is_public = True
        else:
            comment.is_spam = check_spam and comment.check_with_akismet()
            comment.is_public = False
        comment.save()
        return comment
    

class VisibleCommentsManager(CommentsManager):
    def get_query_set(self):
        orig = super(VisibleCommentsManager, self).get_query_set()
        return orig.filter(is_public=True)
    

class PublicComment(models.Model):
    """
    Represents a comment on an article or photo spread, to show up on the
    public-facing site.
    
    May be associated with a UserProfile and/or a name, email combination. If
    we have both a UserProfile and a name, the comment shows only the name 
    and is treated as "anonymous," even though we know who actually posted it.
    """
    
    subject_type = models.ForeignKey(ContentType)
    subject_id   = models.PositiveIntegerField()
    subject      = generic.GenericForeignKey('subject_type', 'subject_id')
    
    user  = models.ForeignKey(UserProfile, null=True, blank=True)
    
    name  = models.CharField(max_length=75, blank=True)
    email = models.EmailField(null=True, blank=True)
    site  = models.URLField(blank=True, verify_exists=True)
    
    time = models.DateTimeField(default=datetime.now)
    text = models.TextField()
    
    ip_address = models.IPAddressField()
    user_agent = models.CharField(blank=True, max_length=100)
    
    is_public = models.BooleanField(default=False)
    is_spam   = models.BooleanField(default=False)
    score = models.IntegerField(default=0)
    
    is_anonymous = property(lambda self: not self.name)
    
    objects = CommentsManager()
    visible = VisibleCommentsManager()
    
    def check_with_akismet(self):
        "Checks whether the comment is spam."
        url = 'http://%s/' % Site.objects.get_current().domain
        akismet_api = akismet.Akismet(key=settings.AKISMET_API_KEY, blog_url=url)
        if akismet_api.verify_key():
            akismet_data = {
                'comment_type': 'comment',
                'comment_author': self.name or self.user.name,
                'comment_author_email': self.email or self.user.email,
                'comment_author_url': self.site,
                'permalink': self.get_absolute_url(),
                'user_ip': self.ip,
                'user_agent': self.user_agent
            }
            text = smart_str(self.text)
            return akismet_api.comment_check(text, data=akismet_data, build_data=True)
        else:
            raise akismet.APIKeyError("Invalid Akismet API key.")
    
    def __unicode__(self):
        return u"on %s by %s" % (self.article.slug, self.user.username)
    
    def get_absolute_url(self):
        return self.article.get_absolute_url + '#c-' + self.pk
    
    class Meta:
        permissions = (
            ('can_post_directly', 'Can post comments without moderation'),
        )
    
