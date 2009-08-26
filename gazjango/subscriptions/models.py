from django.db        import models
from django.db.models import signals, Q
from gazjango.accounts.models import UserProfile, UserKind
from gazjango.registration import signals as registration_signals
import random

class ActiveSubscribersManager(models.Manager):
    def get_query_set(self):
        orig = super(ActiveSubscribersManager, self).get_query_set()
        return orig.filter(unsubscribed=None, is_confirmed=True)
    
	def find_by_email(self, email):
		return self.filter(Q(_email=email) | Q(user__user__email=email))
	

class IssueSubscribersManager(ActiveSubscribersManager):
    def get_query_set(self):
        orig = super(IssueSubscribersManager, self).get_query_set()
        return orig.filter(receive='i')
    

class RSDSubscribersManager(ActiveSubscribersManager):
    def get_query_set(self):
        orig = super(RSDSubscribersManager, self).get_query_set()
        return orig.filter(receive='r')
    

class StaffSubscribersManager(ActiveSubscribersManager):
    def get_query_set(self):
        orig = super(StaffSubscribersManager, self).get_query_set()
        return orig.filter(receive='s')
    

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
        ('r', 'Reserved Students Digest'),
        ('s', 'Staff Minutes'),
    )
    receive = models.CharField(max_length=1, choices=RECEIVE_CHOICES, default='i')
    
    subscribed   = models.DateField(auto_now_add=True)
    modified     = models.DateField(auto_now=True)
    unsubscribed = models.DateField(null=True, blank=True, 
                   help_text='When this user unsubscribed (if they have).')
    last_sent    = models.CharField(max_length=12, blank=True,
                   help_text="The last time an email was successfully sent to this subscriber. " \
                             "For issues, like 2008-11-07; for RSD, like 2008-11-07-1 (for morning).")
    
    plain_text = models.BooleanField(default=False)
    racy_content = models.BooleanField(default=True,
                   help_text='Whether this user should receive sex columns and the like.')
    
    is_confirmed = models.BooleanField(default=True,
                   help_text="Whether this person's email has been confirmed.")
    
    objects = models.Manager()
    active = ActiveSubscribersManager()
    issues = IssueSubscribersManager()
    rsd = RSDSubscribersManager()
    staff = StaffSubscribersManager()
    
    def is_active(self):
        return bool(self.is_confirmed) and not(self.unsubscribed)
    
    def link_to_user(self, user, save=True):
        self._name = ''
        self._email = ''
        self._kind = None
        self.user = user
        if save:
            self.save()
    
    def __unicode__(self):
        return "%s %s" % (self.receive, self.email) + \
               " [%s]" % self.user.username if self.user else ""
    
    class Meta:
        unique_together = (('receive', '_email'),
                           ('receive', 'user'))
    


# when a user's been registered, associate his subscriptions with him
# we wait until registration to make sure that the email is right
def link_subscribers(sender, user, **kwargs):
    profile = user.get_profile()
    for subscriber in Subscriber.objects.filter(email=user.email):
        subscriber.link_to_user(profile)
registration_signals.user_activated.connect(link_subscribers)
