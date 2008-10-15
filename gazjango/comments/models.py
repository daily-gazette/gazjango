from django.db                          import models
from django.db.models                   import Q
from django.utils.encoding              import smart_str
from django.contrib.sites.models        import Site
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes        import generic

from gazjango.accounts.models import UserProfile

from datetime     import datetime
from gazjango.misc.helpers import is_from_swat
from gazjango.misc import akismet
from django.conf   import settings

class CommentsManager(models.Manager):
    def new(self, check_spam=True, pre_approved=False, **data):
        """
        Makes a new comment, checking it for spam if necessary -- that is,
        the user doesn't have the `comments.can_post_directly` permission,
        and `check_spam` is not set to False.
        """
        comment = PublicComment(**data)
        user = comment.user.user if comment.user else None
        
        if comment.is_anonymous or not user.has_perm('comments.can_post_directly'):
            comment.is_spam = check_spam and comment.check_with_akismet()
            comment.is_approved = pre_approved or False
        else:
            comment.is_spam = False
            comment.is_approved = True
        
        previous = PublicComment.objects.filter(subject_id=comment.subject.pk,
                                                subject_type=comment.subject_type)
        if previous.count() > 0:
            comment.number = previous.order_by('-number')[0].number + 1
        else:
            comment.number = 1
        
        comment.score = comment.starting_score()
        comment.save()
        return comment
    

class VisibleCommentsManager(models.Manager):
    def get_query_set(self):
        orig = super(VisibleCommentsManager, self).get_query_set()
        is_visible = Q(is_approved=True) & (Q(score__gt=0) | Q(score=None))
        return orig.filter(is_visible)
    

class PublicComment(models.Model):
    """
    Represents a comment on an article or photo spread, to show up on the
    public-facing site.
    
    May be associated with a UserProfile and/or a name, email combination. If
    we have both a UserProfile and a name, the comment shows only the name 
    and is treated as "anonymous," even though we know who actually posted it.
    
    Comments have a score. If that score is 0 or less, it's been modded down;
    if that score is None, it's been permanently moderated by an editor.
    Whether that moderation was positive or negative depends on the value of
    is_super_shown; if True, it's been permanently shown, if False, it's been
    permanently hidden. (This variable is only consulted if score is None.)
    
    Comments also have a per-article number, starting from one.
    """
    
    subject_type = models.ForeignKey(ContentType)
    subject_id   = models.PositiveIntegerField()
    subject      = generic.GenericForeignKey('subject_type', 'subject_id')
    
    number = models.IntegerField()
    
    user  = models.ForeignKey(UserProfile, null=True, blank=True)
    name  = models.CharField(max_length=100, blank=True)
    email = models.EmailField(null=True, blank=True)
    
    is_anonymous = property(lambda self: bool(self.name))
    display_name = property(lambda self: self.name if self.name else self.user.name)
    
    time = models.DateTimeField(default=datetime.now)
    text = models.TextField()
    
    ip_address = models.IPAddressField(null=True)
    user_agent = models.CharField(max_length=300)
    
    is_approved = models.BooleanField(default=False)
    is_spam     = models.BooleanField(default=False)
    score = models.IntegerField(default=0, null=True)
    shown_forever = models.BooleanField()
    
    def is_visible(self):
        if self.is_approved:
            if self.score is None:
                return self.shown_forever
            else:
                return self.score > 0
        else:
            return False
    
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
                'permalink': url[:-1] + self.get_absolute_url(),
                'user_ip': self.ip_address,
                'user_agent': self.user_agent
            }
            text = smart_str(self.text)
            return akismet_api.comment_check(text, data=akismet_data, build_data=True)
        else:
            raise akismet.APIKeyError("Invalid Akismet API key.")
    
    def starting_score(self):
        from_swat = is_from_swat(user=self.user, ip=self.ip_address)
        if self.user and self.user.user.has_perm('comments.can_post_directly'):
            return 6 if from_swat else 5
        else:
            return 4 if from_swat else 3
    
    def recalculate_score(self):
        score = self.starting_score()
        for vote in self.votes.all():
            val = vote.value
            if val is None:
                self.score = None
                self.shown_forever = vote.positive
                self.save()
                return
            else:
                score += val
        self.score = score
    
    def is_staff(self):
        return False if self.is_anonymous else self.user.is_staff
    
    def status(self):
        if self.is_anonymous:
            if is_from_swat(user=self.user, ip=self.ip_address):
                return "Unregistered, Swarthmore"
            else:
                return "Unregistered, Non-Swarthmore"
        else:
            if self.user.is_staff:
                return "Editor" if self.user.is_editor else "Staff"
            elif is_from_swat(user=self.user, ip=self.ip_address):
                return "Registered, Swarthmore"
            else:
                return "Registered, Non-Swarthmore"
    
    def add_vote(self, positive, user=None, ip=None):
        vote = self.votes.create(positive=positive, user=user, ip=ip)
        self.register_vote(vote)
    
    def register_vote(self, vote):
        vote.set_weight()
        val = vote.value
        if val is None:
            self.score = None
            self.shown_forever = vote.positive
        else:
            self.score += val
        self.save()
    
    def linked_name(self):
        name = self.display_name
        if self.is_staff():
            name = '<a href="%s">%s</a>' % (self.user.get_absolute_url, name)
        return name
    
    def __unicode__(self):
        return u"on %s by %s" % (self.subject.slug, self.display_name)
    
    def get_absolute_url(self):
        return self.subject.get_absolute_url() + \
               ('#c-%d' % self.number) if self.number else ""
    
    class Meta:
        permissions = (
            ('can_post_directly', 'Can post comments without moderation'),
            ('can_moderate_absolutely', 'Can show or hide comments at will')
        )
        unique_together = ('subject_type', 'subject_id', 'number')
    

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
        return self.weight
    
    class Meta:
        # note that null values don't count in uniqueness
        unique_together = (
            ('comment', 'ip'),
            ('comment', 'user')
        )
    
    def __unicode__(self):
        sign = "+" if self.positive else "-"
        vote = str(self.weight) if self.weight else "inf"
        by = self.user.username if self.user else self.ip
        return "%s%s on <comment %s> by %s" % (sign, vote, self.comment, by)
    
