from django.db                  import models
from django.db.models           import permalink
from django.contrib.auth.models import User
from accounts.models            import UserProfile
from articles.models            import Article
from datetime                   import datetime

class Poll(models.Model):
    """A poll. For now, anyone can vote in any poll."""
    # TODO: think about a real permissions system
    # TODO: track whether the same ip is submitted more than once
    # TODO: figure out error handling
    
    name       = models.CharField(max_length=150)
    question   = models.TextField(blank=True)
    slug       = models.SlugField(unique_for_year="time_start")
    time_start = models.DateTimeField(default=datetime.now)
    time_stop  = models.DateTimeField(default=datetime.now)
    allow_anon = models.BooleanField(default=True)
    
    article = models.ForeignKey(Article)
    voters  = models.ManyToManyField(UserProfile)
    
    def voting(self):
        "Whether this poll is open for voting."
        return self.time_start < datetime.now() < self.time_stop
    
    def can_vote(self, user):
        "Whether the given user is allowed to vote in this poll."
        if user.is_authenticated():
            return self.voters.filter(pk=user.get_profile().pk).count() == 0
        else:
           return self.allow_anon # we'll add an IP check later or something
    
    def vote(self, user, option):
        """Casts a user's vote for a particular option and saves.
        
        Returns False if the vote failed, True on success."""
        if not (self.voting() and self.can_vote(user) and option.poll == self):
           return False
        
        option.votes += 1
        option.save()
        
        if user.is_authenticated():
            self.voters.add(user.get_profile())
        else:
            pass # add to IP list
        self.save()
        return True
    
    def results(self):
        """Returns this poll's Options, sorted by votes (most to least).
        
        Ties resolve as the database sees fit."""
        return self.option_set.order_by('-votes')
    
    def __unicode__(self):
        return self.slug
    
    @permalink
    def get_absolute_url(self):
        return ('poll-details', [str(self.time_start.year), self.slug])


class Option(models.Model):
    """An option in a poll."""
    
    poll        = models.ForeignKey(Poll)
    name        = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    votes       = models.IntegerField(blank=True, default=0)
    
    class Meta:
        order_with_respect_to = 'poll'
        unique_together = ('poll', 'name')
    
    def __unicode__(self):
        return self.name
    
