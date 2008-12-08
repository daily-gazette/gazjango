import django.db
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
        Makes a new comment, dealing with spam checking and pre-approval
        as necessary.
        
        Comments from Swarthmore IPs or registered users are not spam-checked.
        
        Comments from Swat IPs and non-anonymous users who haven't lost the
        can_post_directly permission are pre-approved (as per `pre_approved`).
        """
        comment = PublicComment(**data)
        
        anon = comment.is_anonymous
        user = comment.user.user if comment.user else None
        needs_moderation = user and not user.has_perm('comments.can_post_directly')
        from_swat = is_from_swat(user=comment.user, ip=comment.ip_address)
        
        if not from_swat and not user:
            comment.is_spam = check_spam and comment.check_with_akismet()
        else:
            comment.is_spam = False
        
        if needs_moderation or (anon and not from_swat):
            comment.is_approved = pre_approved
        else:
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
    
    def for_article(self, article, user, ip, allow_spam=False, spec=models.Q()):
        """
        Returns `article`s comments, in the format used by the comments
        template: [(comment, status)], where `status` is 1 if the viewer
        has voted that comment up, 0 if he hasn't voted on it, and -1 if
        he's voted it down.
        
        The comments can optionally be filtered by `spec`.
        
        Spam comments are excluded by default; `allow_spam` changes this
        behavior.
        """
        spec &= models.Q(is_spam=False)
        comments = article.comments.filter(spec).select_related(depth=1)
        return [(c, c.vote_status(user=user, ip=ip)) for c in comments]

class VisibleCommentsManager(CommentsManager):
    def get_query_set(self):
        orig = super(VisibleCommentsManager, self).get_query_set()
        return orig.filter(is_approved=True, is_spam=False, score__gt=0)
    

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
    display_name = property(lambda self: self.name or (self.user.name if self.user else ''))
    
    time = models.DateTimeField(default=datetime.now)
    text = models.TextField()
    
    ip_address = models.IPAddressField(null=True)
    user_agent = models.CharField(max_length=300)
    
    is_approved = models.BooleanField(default=False)
    is_spam     = models.BooleanField(default=False)
    score = models.IntegerField(default=0, null=True)
    
    def is_visible(self):
        return self.is_approved and not self.is_spam and self.score > 0
    
    objects = CommentsManager()
    visible = VisibleCommentsManager()
    
    def _akismet_framework(self, function):
        url = 'http://%s/' % Site.objects.get_current().domain
        akismet_api = akismet.Akismet(key=settings.AKISMET_API_KEY, blog_url=url)
        if akismet_api.verify_key():
            akismet_data = {
                'comment_type': 'comment',
                'comment_author': self.name or self.user.name,
                'comment_author_email': self.user.email if self.user else self.email,
                'permalink': url[:-1] + self.get_absolute_url(),
                'user_ip': self.ip_address,
                'user_agent': self.user_agent
            }
            text = smart_str(self.text)
            return function(akismet_api, text, data=akismet_data, build_data=True)
        else:
            raise akismet.APIKeyError("Invalid Akismet API key.")
    
    def check_with_akismet(self):
        "Checks whether the comment is spam."
        return self._akismet_framework(akismet.Akismet.comment_check)
    
    def mark_as_spam(self):
        "Marks a comment which Akismet said was good as spam."
        self._akismet_framework(akismet.Akismet.submit_spam)
        self.is_spam = True
        self.save()
    
    def mark_as_ham(self):
        "Marks a comment which Akismet said was spam as good."
        self._akismet_framework(akismet.Akismet.submit_ham)
        self.is_spam = False
        self.save()
    
    def starting_score(self):
        from_swat = is_from_swat(user=self.user, ip=self.ip_address)
        directly = self.user and self.user.user.has_perm('comments.can_post_directly')
        if not self.is_anonymous and directly:
            return 6 if from_swat else 5
        else:
            return 4 if from_swat else 3
    
    def recalculate_score(self):
        self.score = self.starting_score()
        self.score += sum(vote.value for vote in self.votes.all())
        self.save()
    
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
                return "Editor" if self.user.is_editor() else "Staff"
            elif is_from_swat(user=self.user, ip=self.ip_address):
                return "Registered, Swarthmore"
            else:
                return "Registered, Non-Swarthmore"
    
    def get_vote(self, user=None, ip=None):
        try:
            if user is not None:
                return self.votes.get(user=user)
            else:
                return self.votes.get(ip=ip, user=None)
        except CommentVote.DoesNotExist:
            return None
    
    def vote(self, positive, user=None, ip=None):
        """
        Casts a vote for `user` and `ip`. If a vote is already present, override
        it; if there's a vote and `positive` is None, clear it. If the voter is
        an editor, update their custom_weight.
        """
        status = self.vote_status(user=user, ip=ip)
        if status is None: # hasn't voted yet
            if positive is not None:
                vote = self.votes.create(positive=positive, user=user, ip=ip)
                self.register_vote(vote)
        else:
            vote = self.get_vote(user=user, ip=ip)
                        
            if positive is None:
                vote.delete()
            else:
                if user and user.user.has_perm('comments.can_moderate_absolutely'):
                    vote.custom_value = vote.custom_value or vote.value
                    vote.custom_value += (1 if positive else -1) * 2
                    vote.save()
                else:
                    vote.positive = positive
                    vote.set_weight() # in case it's changed
            self.recalculate_score()
    
    def register_vote(self, vote):
        vote.set_weight()
        self.score += vote.value
        self.save()
    
    def vote_status(self, user=None, ip=None):
        """
        Returns `user`/`ip`'s vote on this comment: None if they haven't
        voted, otherwise the value.
        """
        vote = self.get_vote(user=user, ip=ip)
        return vote.value if vote else None
    
    def linked_name(self):
        name = self.display_name
        if self.is_staff():
            name = '<a href="%s">%s</a>' % (self.user.get_absolute_url(), name)
        return name
    
    def article_name(self):
        try:
            return self.subject.headline
        except:
            return "<>"
    
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
    Represents a user / IP's vote for or against a given comment.
    """
    comment = models.ForeignKey(PublicComment, related_name="votes")
    
    user = models.ForeignKey(UserProfile, null=True)
    ip   = models.IPAddressField(blank=True, null=True)
    
    positive = models.BooleanField()
    weight   = models.IntegerField(default=1)
    custom_value = models.IntegerField(null=True, default=None,
                   help_text="Overrides the vote's weight if set; used for editors.")
    
    def _value(self):
        if self.custom_value is not None:
            return self.custom_value
        else:
            return (1 if self.positive else -1) * self.weight
    value = property(_value)
    
    def set_weight(self):
        """
        Sets the weight of this vote. Anonymous voters get 1, regular
        users get 2, Swat users get 3, staff get 4. Editors get however
        many points they want. :)
        """ 
        if not self.user:
            self.weight = 1
        elif self.user.user.has_perm('comments.can_moderate_absolutely'):
            # don't bother with weight
            if self.custom_value is None:
                self.custom_value = (1 if self.positive else -1) * 4
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
            ('comment', 'user'),
            ('comment', 'user', 'ip'),
        )
    
    def __unicode__(self):
        by = self.user.username if self.user else self.ip
        return "%+d on <comment %s> by %s" % (self.value, self.comment, by)
    
