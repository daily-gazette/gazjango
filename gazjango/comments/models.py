from django.db                          import models
from django.db.models                   import signals
from django.dispatch                    import dispatcher
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
        user = comment.user.user
        
        if comment.is_anonymous or not user.has_perm('comments.can_post_directly'):
            comment.is_spam = check_spam and comment.check_with_akismet()
            comment.is_approved = False
        else:
            comment.is_spam = False
            comment.is_approved = True
        
        comment.score = comment.starting_score()
        comment.save()
        return comment
    

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
    
    time = models.DateTimeField(default=datetime.now)
    text = models.TextField()
    
    ip_address = models.IPAddressField(null=True)
    user_agent = models.CharField(max_length=100)
    
    is_approved = models.BooleanField(default=False)
    is_spam     = models.BooleanField(default=False)
    score = models.IntegerField(default=0, null=True)
    
    is_anonymous = property(lambda self: not self.name)
    
    def is_visible(self):
        if self.is_approved or self.score is None:
            return True
        else:
            return self.score > 0
    
    objects = CommentsManager()
    
    def check_with_akismet(self):
        "Checks whether the comment is spam."
        url = 'http://%s/' % Site.objects.get_current().domain
        akismet_api = akismet.Akismet(key=settings.AKISMET_API_KEY, blog_url=url)
        if akismet_api.verify_key():
            akismet_data = {
                'comment_type': 'comment',
                'comment_author': self.name or self.user.name,
                'comment_author_email': self.email or self.user.email,
                'permalink': self.get_absolute_url(),
                'user_ip': self.ip_address,
                'user_agent': self.user_agent
            }
            text = smart_str(self.text)
            return akismet_api.comment_check(text, data=akismet_data, build_data=True)
        else:
            raise akismet.APIKeyError("Invalid Akismet API key.")
    
    def starting_score(self):
        from_swat = self.user.is_from_swat(ip=self.ip_address)
        if self.user and self.user.user.has_perm('comments.can_post_directly'):
            return 6 if from_swat else 5
        else:
            return 4 if from_swat else 3
    
    def recalculate_score(self):
        score = self.starting_score()
        for vote in self.votes.all():
            val = vote.value
            if val is None:
                if vote.positive:
                    self.score = None
                else:
                    self.is_approved = False
                self.save()
                return
            else:
                score += val
        self.score = score
    
    def __unicode__(self):
        return u"on %s by %s" % (self.subject.slug, self.user.username)
    
    def get_absolute_url(self):
        return self.subject.get_absolute_url + '#c-' + self.pk
    
    class Meta:
        permissions = (
            ('can_post_directly', 'Can post comments without moderation'),
            ('can_moderate_absolutely', 'Can show or hide comments at will')
        )
    

class CommentVote(models.Model):
    """
    Represent's a user / IP's vote for or against a given comment.
    """
    comment = models.ForeignKey(PublicComment, related_name="votes")
    positive = models.BooleanField()
    
    user = models.ForeignKey(UserProfile, null=True)
    ip   = models.IPAddressField(blank=True, null=True)
    
    weight = models.IntegerField(null=True, default=1)
    
    def _value(self):
        if self.weight is None:
            return None
        else:
            return (1 if self.positive else -1) * self.weight
    
    value = property(_value)
    
    def set_weight(self):
        """
        Sets the weight of this vote. Anonymous voters get 1, regular
        users get 2, Swat users get 3, staff get 4. Editors get override
        power, aka null. :)
        """ 
        if not self.user:
            self.weight = 1
        elif self.user.user.has_perm('comments.can_moderate_absolutely'):
            self.weight = None
        elif self.user.user.is_staff:
            self.weight = 4
        elif self.user.is_from_swat(ip=self.ip):
            self.weight = 3
        else:
            self.weight = 2
        self.save()
    
    class Meta:
        # note that null values don't count in uniqueness
        unique_together = (
            ('comment', 'ip'),
            ('comment', 'user')
        )
    
    def __unicode__(self):
        vote = ("+" if self.positive else "-") + str(self.weight())
        by = self.user.username if self.user else self.ip
        return "%s on <comment %s> by %s" % (vote, self.comment, by)
    

def register_vote(sender, instance):
    instance.set_weight()
    val = instance.value
    if val is None:
        instance.comment.score = None
    else:
        instance.comment.score += val
    instance.comment.save()

dispatcher.connect(register_vote, signal=signals.post_init, sender=CommentVote)
