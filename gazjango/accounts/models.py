from django.db                  import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    "Extra information about users."
    user      = models.ForeignKey(User, unique=True)
    bio       = models.TextField(blank=True)
    contact   = models.TextField(blank=True)
    # many-to-many Articles


class Position(models.Model):
    "A position in the organization: Staff Reporter, Editor-in-Chief, etc."
    name       = models.CharField(blank=True, max_length=40)


class PositionHeld(models.Model):
    """A user's holding of a position.
    
    Contains information about when the position was held. If a position is
    still held, date_end will be null."""
    
    user_profile = models.ForeignKey(UserProfile, related_name='positions')
    position     = models.ForeignKey(Position)
    date_start   = models.DateField()
    date_end     = models.DateField(null=True, blank=True)
