from django.db                  import models
from django.db.models           import Q, permalink
from django.contrib.auth.models import User
from datetime                   import datetime, date

class UserProfile(models.Model):
    "Extra information about users."
    user    = models.ForeignKey(User, unique=True)
    bio     = models.TextField(blank=True, null=True)
    phone   = models.PhoneNumberField(blank=True, null=True)
    contact = models.TextField(blank=True, null=True)
    # many-to-many Articles, has-many PositionsHeld
    
    name = property(lambda self: self.user.get_full_name())
    username = property(lambda self: self.user.username)
    email = property(lambda self: self.user.email)
    
    def position_at(self, date):
        """Returns the highest-ranked of this user's Positions at date."""
        held = self.positions_held_at(date).order_by("-position__rank")[0]
        return held.position
    
    def position(self):
        """Returns the highest-ranked of the user's Positions as of now."""
        return self.position_at(date.today())
    
    
    def positions_held_at(self, date):
        """Returns PositionsHeld the user had at the given date."""
        query_end = Q(date_end__isnull = True) | Q(date_end__gte=date)
        return self.positions_held.filter(query_end & Q(date_start__lte=date))
    
    def positions_at(self, date):
        """Returns Positions the user held at the given date."""
        helds = self.positions_held_at(date).select_related(depth=1)
        return [p.position for p in helds]
    
    
    def current_positions_held(self):
        "Returns PositionHelds currently held by this user."
        return self.positions_held_at(date.today())
    
    def current_positions(self):
        "Returns Positions currently held by this user."
        return self.positions_at(date.today())
    
    
    def add_position(self, position, date_start=None, date_end=None):
        "Adds a new PositionHeld relation for this user."
        if date_start is None: date_start = date.today()
        self.positions_held.add(PositionHeld.objects.create(
            user_profile = self,       position    = position,
            date_start   = date_start, date_end    = date_end))
    
    def __unicode__(self):
        return self.user.username
    
    @permalink
    def get_absolute_url(self):
        return ('accounts.views.user_details', [self.user.username])
    


class Position(models.Model):
    """A position in the organization: Staff Reporter, Editor-in-Chief, etc.
    
    Has a rank, which is used for precedence in choosing the "correct" title
    when there is more than one choice. For example, if John is currently both
    arts editor and a photographer, being arts editor takes precedence and will
    show up next to his name when he writes a story."""
    
    name = models.CharField(max_length=40, unique=True)
    rank = models.IntegerField()
    
    def __unicode__(self):
        return self.name
    

class PositionHeld(models.Model):
    """A user's holding of a position.
    
    Contains information about when the position was held. If a position is
    still held, date_end will be null."""
    
    user_profile = models.ForeignKey(UserProfile, related_name='positions_held')
    position     = models.ForeignKey(Position, related_name='holdings')
    date_start   = models.DateField(default=date.today)
    date_end     = models.DateField(null=True, blank=True)
    
    name = property(lambda self: self.position.name)
    rank = property(lambda self: self.position.rank)
    
    def __unicode__(self):
        return "%s (by %s)" % (self.position.__unicode__(),
                               self.user_profile.__unicode__())
    
