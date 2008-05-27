from django.db                  import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    "Extra information about users."
    user      = models.ForeignKey(User, unique=True)
    bio       = models.TextField(blank=True)
    positions = models.ManyToManyField('Position')
    contact   = models.TextField(blank=True)
    # many-to-many Articles


class Position(models.Model):
    "A position in the organization: Staff Reporter, Editor-in-Chief, etc."
    name       = models.CharField(blank=True, max_length=40)
    time_start = models.DateField()
    time_end   = models.DateField() # None when still held
