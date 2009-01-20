from django.db                  import models
from django.db.models           import Q, permalink
from django.contrib.auth.models import User
from gazjango.misc.helpers import ip_from_swat
from datetime              import datetime, date

class UserKind(models.Model):
    """
    A kind of user. 
    
    There is at most one kind per class year, plus faculty/staff,
    parents, specs, and other.
    """
    KINDS = (
        ('s', 'Student'),
        ('a', 'Alum'),
        ('f', 'Faculty/Staff'),
        ('p', 'Parent'),
        ('k', 'Prospective Student'),
        ('o', 'Other')
    )
    kind = models.CharField(max_length=1, choices=KINDS)
    year = models.IntegerField(null=True) # for students/alumni
    
    class Meta:
        unique_together = ('kind', 'year')
        ordering = ('kind', '-year')
    
    def __unicode__(self):
        return self.get_kind_display() + \
               (" (%s)" % self.year if self.year else "")
    

class ContactMethod(models.Model):
    """
    A way to get in touch with someone. In general, this will probably
    be mainly be used only for the various IM services. We also use it
    for phone numbers, though, for consistency's sake.
    """
    name = models.CharField(max_length=40)
    
    def __unicode__(self):
        return self.name
    

class ContactItem(models.Model):
    """
    A user's contact information for a given ContactMethod. For example,
    if Joe has an MSN screenname and an AIM one, he'd have one of these
    for each. He'd also probably have one for his cell.
    """
    user   = models.ForeignKey('UserProfile', related_name="contact_items")
    method = models.ForeignKey(ContactMethod, related_name="items")
    value  = models.CharField(max_length=50)
    
    def __unicode__(self):
        return "%s on %s" % (self.value, self.method)
    

class ProfilesManager(models.Manager):
    def create_lite_user(self, first, last):
        "Creates a bare-bones user."
        username = base = ("%s_%s" % (first, last)).lower().replace(" ", "_")
        num = 0
        while User.objects.filter(username=username).count() > 0:
            num += 1
            username = base + str(num)
        
        user = User.objects.create_user(username, 'unkwown@nowhere.com')
        user.first_name, user.last_name = first, last
        user.save()
        profile = user.userprofile_set.create()
        return profile
    
    def username_for_name(self, name, create=False):
        """
        Returns the username for the user whose name is `name`. If there
        is no such user and `create` is True, make one.
        
        If there's more than one space, try to figure it out, but it might
        be kind of flakey.
        """
        split = name.split()
        if len(split) < 2:
            raise User.DoesNotExist
        elif len(split) == 2:
            first, last = split
        else:
            for i in range(1, len(split)):
                first = ' '.join(split[:i])
                last  = ' '.join(split[i:])
                matches = User.objects.filter(
                    first_name__iexact=first,
                    last_name__iexact=last
                )
                if matches.count():
                    break
        
        try:
            u = User.objects.get(first_name__iexact=first, last_name__iexact=last)
            return u.username
        except User.DoesNotExist:
            if create:
                return self.create_lite_user(first, last).username
            else:
                raise
        

class UserProfile(models.Model):
    "Lots of extra information about users."
    user = models.ForeignKey(User, unique=True)
    kind = models.ForeignKey(UserKind, null=True)
    
    bio     = models.TextField(blank=True, null=True)
    awards  = models.TextField(blank=True, null=True)
    picture = models.ForeignKey('media.ImageFile', blank=True, null=True)
    positions = models.ManyToManyField('Position', through='Holding', related_name="holdings")
    
    name     = property(lambda self: self.user.get_full_name())
    username = property(lambda self: self.user.username)
    email    = property(lambda self: self.user.email)
    is_staff = property(lambda self: self.user.is_staff)
    
    facebook_id = models.IntegerField('Facebook User ID #', blank=True, null=True, unique=True)
    
    def is_editor(self):
        return self.current_positions().filter(is_editor=True).count() > 0
    
    objects = ProfilesManager()
    
    _from_swat = models.BooleanField(default=False)
    def is_from_swat(self, ip=None):
        if self._from_swat:
            return True
        elif self.email.endswith('swarthmore.edu') or ip_from_swat(ip):
            self._from_swat = True
            self.save()
            return True
        else:
            return False
    
    EMAIL_DOMAIN = '@swarthmore.edu'
    def abbreviated_email(self):
        if self.email.endswith(self.EMAIL_DOMAIN):
            return self.email[:-len(self.EMAIL_DOMAIN)]
        else:
            return self.email
    
    def published_articles(self):
        return self.articles.filter(status='p')
    
    def positions_at(self, date):
        """Returns the Positions the user had at the given date."""
        null_end = Q(holding__date_end__isnull = True)
        later_end = Q(holding__date_end__gte=date)
        started = Q(holding__date_start__lte=date)
        return self.positions.filter(started & (later_end | null_end))
    
    def current_positions(self):
        "Returns Positions currently held by this user."
        return self.positions_at(date.today())
    
    def position_at(self, date):
        """Returns the highest-ranked of this user's Positions at date."""
        try:
            return self.positions_at(date).order_by("-rank")[0]
        except IndexError:
            return None
    
    def position(self):
        """Returns the highest-ranked of the user's Positions as of now."""
        return self.position_at(date.today())
    
    
    def add_position(self, position, date_start=None, date_end=None):
        "Adds a new position for this user."
        Holding.objects.create(
            user_profile = self,
            position = position,
            date_start = date_start or date.today(),
            date_end   = date_end
        )
    
    
    def claimed(self):
        """Returns this user's claimed story concepts."""
        return self.concepts.exclude(status='p')
    
    def __unicode__(self):
        return "%s (%s)" % (self.name, self.username)
    
    @permalink
    def get_absolute_url(self):
        return ('accounts.views.user_details', [self.user.username])
    
    class Meta:
        permissions = (
            ('can_access_admin', 'Can access the reporter admin.'),
        )
        ordering = ('-user__is_staff', 'user__last_name', 'user__first_name', 'user__username')
    

class Position(models.Model):
    """
    A position in the organization: Staff Reporter, Editor-in-Chief, etc.
    
    Has a rank, which is used for precedence in choosing the "correct" title
    when there is more than one choice. For example, if John is currently both
    arts editor and a photographer, being arts editor takes precedence and will
    show up next to his name when he writes a story.
    
    Also marks whether this position implies editorship.
    """
    
    name = models.CharField(max_length=40, unique=True)
    rank = models.IntegerField()
    is_editor = models.BooleanField(default=False)
    
    def __unicode__(self):
        return self.name
    

class Holding(models.Model):
    """
    A user's holding of a position.
    
    Contains information about when the position was held. If a position is
    still held with no definite end date, date_end will be null.
    """
    
    user_profile = models.ForeignKey(UserProfile)
    position     = models.ForeignKey(Position)
    date_start   = models.DateField(default=date.today)
    date_end     = models.DateField(null=True, blank=True)
    
    name = property(lambda self: self.position.name)
    rank = property(lambda self: self.position.rank)
    
    def __unicode__(self):
        return "%s (by %s)" % (self.position.__unicode__(),
                               self.user_profile.__unicode__())
    
    class Meta:
        ordering = ['date_start']
    
