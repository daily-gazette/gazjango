from django.db                  import models
from django.db.models           import Q, permalink
from django.contrib.auth.models import User
from datetime                   import datetime, date

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
    
    def __unicode__(self):
        return self.kind + (" (%s)" % self.year if self.year else "")
    

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
    

class UserProfile(models.Model):
    "Lots of extra information about users."
    user = models.ForeignKey(User, unique=True)
    bio  = models.TextField(blank=True, null=True)
    kind = models.ForeignKey(UserKind)
    
    name     = property(lambda self: self.user.get_full_name())
    username = property(lambda self: self.user.username)
    email    = property(lambda self: self.user.email)
    
    positions = models.ManyToManyField('Position', through='Holding', related_name="holdings")
    
    _from_swat = models.BooleanField(default=False)
    
    def is_from_swat(self, ip=None):
        if self._from_swat:
            return True
        elif self.email.endswith('swarthmore.edu') or \
                            ip and ip.startswith(settings.SWARTHMORE_IP_BLOCK):
            self._from_swat = True
            self.save()
            return True
        else:
            return False
    
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
        return self.positions_at(date).order_by("-rank")[0]
    
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
    
    def __unicode__(self):
        return self.user.username
    
    @permalink
    def get_absolute_url(self):
        return ('accounts.views.user_details', [self.user.username])
    


class Position(models.Model):
    """
    A position in the organization: Staff Reporter, Editor-in-Chief, etc.
    
    Has a rank, which is used for precedence in choosing the "correct" title
    when there is more than one choice. For example, if John is currently both
    arts editor and a photographer, being arts editor takes precedence and will
    show up next to his name when he writes a story.
    """
    
    name = models.CharField(max_length=40, unique=True)
    rank = models.IntegerField()
    
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
    
