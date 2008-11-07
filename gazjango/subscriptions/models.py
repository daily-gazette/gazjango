from django.db        import models
from django.db.models import signals
from gazjango.accounts.models import UserProfile, UserKind
import random

class ActiveSubscribersManager(models.Manager):
    def get_query_set(self):
        orig = super(ActiveSubscribersManager, self).get_query_set()
        return orig.filter(unsubscribed=None)
    

class IssueSubscribersManager(ActiveSubscribersManager):
    def get_query_set(self):
        orig = super(IssueSubscribersManager, self).get_query_set()
        return orig.filter(receive='i')
    

class RSDSubscribersManager(ActiveSubscribersManager):
    def get_query_set(self):
        orig = super(RSDSubscribersManager, self).get_query_set()
        return orig.filter(receive='r')
    

class Subscriber(models.Model):
    """
    A subscriber, who gets issues in their inbox when we publish. Either 
    linked to a UserProfile or has a name, email, and UserKind.
    
    When someone unsubscribes, we set `unsubscribed` to that day and leave
    their data around, so that we can get pretty graphs of subscription
    numbers or whatever.
    
    The confirmation key is quasi-secret: it serves in lieu of a password
    for management things (unsubscribing, changing preferences).
    """
    _name  = models.CharField(max_length=40, blank=True)
    _email = models.EmailField(null=True, default=None, blank=True)
    _kind  = models.ForeignKey(UserKind, null=True, blank=True)
    user = models.ForeignKey(UserProfile, null=True, blank=True,
           help_text="A user to link this subscription to. If this is set, *don't* " \
                     "set name/email/kind; they're inherited from the user.")
    
    name  = property(lambda self: self.user.name  if self.user else self._name)
    email = property(lambda self: self.user.email if self.user else self._email)
    kind  = property(lambda self: self.user.kind  if self.user else self._kind)
    
    RECEIVE_CHOICES = (
        ('i', 'Issues'),
        ('r', 'Reserved Students Digest')
    )
    receive = models.CharField(max_length=1, choices=RECEIVE_CHOICES, default='i')
    
    subscribed   = models.DateField(auto_now_add=True)
    modified     = models.DateField(auto_now=True)
    unsubscribed = models.DateField(null=True, blank=True, 
                   help_text='When this user unsubscribed (if they have).')
    
    plain_text = models.BooleanField(default=False)
    racy_content = models.BooleanField(default=True,
                   help_text='Whether this user should receive sex columns and the like.')
    
    is_confirmed = models.BooleanField(default=True,
                   help_text="Whether this person's email has been confirmed.")
    confirmation_key = models.CharField(max_length=15)
    
    objects = models.Manager()
    active = ActiveSubscribersManager()
    issues = IssueSubscribersManager()
    rsd = RSDSubscribersManager()
    
    def is_active(self):
        return self.is_confirmed and not self.unsubscribed
    
    def randomize_confirmation_key(self):
        chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        key = ''.join(random.choice(chars) for x in xrange(15))
        self.confirmation_key = key
    
    def __unicode__(self):
        if self.user:
            return "%s (linked to %s)" % (self.email, self.user.username)
        else:
            return self.email
    
    class Meta:
        unique_together = (('receive', '_email'),
                           ('receive', 'user'))

def set_default_key(sender, instance, **kwargs):
    if not instance.confirmation_key:
        instance.randomize_confirmation_key()

signals.post_init.connect(set_default_key, sender=Subscriber)
