from django.db                  import models
from django.contrib.auth.models import User
from datetime                   import datetime

class UserProfile(models.Model):
    "Extra information about users."
    user    = models.ForeignKey(User, unique=True)
    bio     = models.TextField(blank=True)
    contact = models.TextField(blank=True)
    # many-to-many Articles, has-many PositionsHeld
    
    def current_positions(self):
        "Returns positions currently held by this user."
        return self.positions.filter(date_end=None).all()
    
    def add_position(self, position, date_start=None, date_end=None):
        "Adds a new PositionHeld relation for this user."
        if date_start is None: date_start = datetime.today()
        self.positions.add(PositionHeld.objects.create(
            user_profile = self,       position    = position,
            date_start   = date_start, date_end    = date_end))
    
    def __unicode__(self):
        return self.user.username
    


class Position(models.Model):
    "A position in the organization: Staff Reporter, Editor-in-Chief, etc."
    name = models.CharField(max_length=40, unique=True)
    
    def __unicode__(self):
        return self.name
    

class PositionHeld(models.Model):
    """A user's holding of a position.
    
    Contains information about when the position was held. If a position is
    still held, date_end will be null."""
    
    user_profile = models.ForeignKey(UserProfile, related_name='positions')
    position     = models.ForeignKey(Position, related_name='holdings')
    date_start   = models.DateField()
    date_end     = models.DateField(null=True, blank=True)
    
    def __unicode__(self):
        return "%s (by %s)" % (self.position.__unicode__(),
                               self.user_profile.__unicode__())
    
