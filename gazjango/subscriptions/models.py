from django.db        import models
from django.db.models import signals, Q
from gazjango.accounts.models import UserProfile, UserKind
from registration.signals import user_activated

class SubscribersManager(models.Manager):
    def find_by_email(self, email):
        return self.filter(Q(_email__istartswith=email) | Q(user__user__email__istartswith=email))
    

class ActiveSubscribersManager(SubscribersManager):
    def get_query_set(self):
        orig = super(ActiveSubscribersManager, self).get_query_set()
        return orig.filter(unsubscribed=None, is_confirmed=True)

    
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
    

class AllIssueSubscribersManager(SubscribersManager):
    def get_query_set(self):
        orig = super(AllIssueSubscribersManager, self).get_query_set()
        return orig.filter(receive='i')
    

class AllRSDSubscribersManager(SubscribersManager):
    def get_query_set(self):
        orig = super(AllRSDSubscribersManager, self).get_query_set()
        return orig.filter(receive='r')
    


class Subscriber(models.Model):
    """
    A subscriber, who gets issues in their inbox when we publish. Either 
    linked to a UserProfile or has a name, email, and UserKind.
    
    When someone unsubscribes, we set `unsubscribed` to that day and leave
    their data around, so that we can get pretty graphs of subscription
    numbers or whatever.
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
    
    objects = SubscribersManager()
    active = ActiveSubscribersManager()
    issues = IssueSubscribersManager()
    rsd = RSDSubscribersManager()
    staff = StaffSubscribersManager()
    rsd_all = AllRSDSubscribersManager()
    issues_all = AllIssueSubscribersManager()
    
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
        base = self.email
        base += "(%s)" % self.user.username if self.user else ""
        return "%s [%s]" % (base, self.receive)
    
    class Meta:
        unique_together = (('receive', '_email'),
                           ('receive', 'user'))
    


# When a user's been registered, associate his subscriptions with him if he
# already has some. Also, activate any subscriptions that haven't yet been
# activated, since we know that his email is correct. We shouldn't associate
# (or confirm) subscribers before user activation, since they might not really
# have the email address they signed up with.
def setup_subscribers(sender, user, **kwargs):
    profile = user.get_profile()
    for subscriber in Subscriber.objects.filter(user=profile):
        subscriber.is_confirmed = True
        subscriber.save()

    for subscriber in Subscriber.objects.find_by_email(user.email):
        subscriber.link_to_user(profile)
user_activated.connect(setup_subscribers)
