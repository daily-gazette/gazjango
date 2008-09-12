from django.db        import models
from django.db.models import signals
from accounts.models import UserProfile, UserKind
import random

class IssueType(models.Model):
    """
    What template should be used for this subscriber's issues.
    
    Include plain text, regular HTML with images, optimized-for-swatmail,
    full-article-text.
    """
    name = models.CharField(max_length=60)
    slug = models.SlugField(unique=True)
    
    def __unicode__(self):
        return self.slug
    

class ActiveSubscribersManager(models.Manager):
    def get_query_set(self):
        orig = super(ActiveSubscribersManager, self).get_query_set()
        return orig.filter(unsubscribed=None)
    

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
    _name  = models.CharField(max_length=40)
    _email = models.EmailField(unique=True)
    _kind  = models.ForeignKey(UserKind, null=True)
    user = models.ForeignKey(UserProfile, null=True, unique=True)
    
    name  = property(lambda self: self.user.name  if self.user else self._name)
    email = property(lambda self: self.user.email if self.user else self._email)
    kind  = property(lambda self: self.user.kind  if self.user else self._kind)
    
    subscribed   = models.DateField(auto_now_add=True)
    modified     = models.DateField(auto_now=True)
    unsubscribed = models.DateField(null=True)
    
    issue_type   = models.ForeignKey(IssueType)
    racy_content = models.BooleanField(default=True)
    
    is_confirmed = models.BooleanField(default=False)
    confirmation_key = models.CharField(max_length=15)
    
    objects = models.Manager()
    active = ActiveSubscribersManager()
    
    def randomize_confirmation_key(self):
        chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        key = ''.join(random.choice(chars) for x in xrange(30))
        self.confirmation_key = key
    
    def __unicode__(self):
        if self.user:
            return "%s (linked to %s)" % (self.email, self.user.username)
        else:
            return self.email
    

def set_default_key(sender, instance, **kwargs):
    if not instance.confirmation_key:
        instance.randomize_confirmation_key()
        instance.save()

signals.post_init.connect(set_default_key, sender=Subscriber)
