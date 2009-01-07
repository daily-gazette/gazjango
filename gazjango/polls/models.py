from django.db                  import models
from django.contrib.auth.models import User
from gazjango.accounts.models   import UserProfile
from gazjango.articles.models   import Article

from gazjango.polls.exceptions import *
from datetime                  import datetime

class Poll(models.Model):
    """A poll."""
    
    name       = models.CharField(max_length=150)
    question   = models.TextField(blank=True)
    slug       = models.SlugField(unique_for_year="time_start")
    time_start = models.DateTimeField(default=datetime.now)
    time_stop  = models.DateTimeField(default=datetime.now, null=True)
    allow_anon = models.BooleanField(default=True)
    
    articles = models.ManyToManyField(Article, related_name="polls")
    
    def voting(self):
        "Whether this poll is open for voting."
        if self.time_stop:
            return self.time_start < datetime.now() < self.time_stop
        else:
            return self.time_start < datetime.now()
    
    def has_voted(self, user=None, ip=None):
        "Whether the given user / ip has already voted."
        if user:
            return self.votes.filter(user=user).count() > 0
        else:
            return self.votes.filter(user=None, ip=ip).count() > 0
    
    def vote_allowed(self, user=None, ip=None):
        """
        Whether the user could ever vote in this poll (regardless of whether
        they already have.)
        """
        return bool(user) or self.allow_anon
    
    def can_vote(self, user=None, ip=None):
        "Whether the given UserProfile / ip is allowed to vote in this poll."
        return self.vote_allowed(user, ip) and not self.has_voted(user, ip)
    
    def vote(self, option, user=None, ip=None):
        """
        Casts a user's vote for a particular option and saves.
        
        Note that the `user` argument should be a UserProfile.
        """
        if user:
            args = { 'user': user }
        else:
            args = { 'ip': ip }
        
        if not self.voting():
            raise NotVoting
        
        if option.poll != self:
            raise PollMismatch
        
        if self.has_voted(**args):
            raise AlreadyVoted
        
        if not self.vote_allowed(**args):
            raise PermissionDenied
        
        return self.votes.create(option=option, **args)
    
    def __unicode__(self):
        return self.slug
    
    def get_absolute_url(self):
        return self.article.get_absolute_url() + '#poll-' + self.pk
    

class PollOption(models.Model):
    """An option in a poll."""
    poll = models.ForeignKey(Poll, related_name="options")
    name = models.CharField(max_length=100)
    
    def num_votes(self):
        return self.votes.count()
    
    def vote_percent(self):
        return int(round(100 * self.num_votes() / self.poll.votes.count()))
    
    class Meta:
        order_with_respect_to = 'poll'
        unique_together = ('poll', 'name')
    
    def __unicode__(self):
        return self.name
    

class PollVote(models.Model):
    poll = models.ForeignKey(Poll, related_name="votes")
    option = models.ForeignKey(PollOption, related_name="votes")
    
    user = models.ForeignKey(UserProfile, null=True, related_name="votes")
    ip   = models.IPAddressField(null=True, blank=True)
    
    name = models.CharField(max_length=30)
    hostname = models.CharField(max_length=60)
    time = models.DateTimeField(blank=True, default=datetime.now)
    
    class Meta:
        # nulls don't count for unique_together
        unique_together = (
            ('poll', 'user'),
            ('poll', 'ip')
        )
    
    def __unicode__(self):
        return "%s by %s" % \
               (self.option.name, self.user.username if self.user else self.ip)
    
