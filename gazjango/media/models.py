from datetime         import datetime
from django.db        import models
from django.db.models import permalink
from gazjango.accounts.models import UserProfile

class MediaBucket(models.Model):
    """
    A bucket containing media files related in some way.
    
    Examples include: photos taken at a given event, Suzy Q.'s miscellaneous 
    photos of the day, photos related to a certain article, etc.
    """
    
    name = models.CharField(blank=True, max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    
    def __unicode__(self):
        return self.slug
    

# TODO: media should be stored in S3 / Fedora Commons / the filesystem by
#       bucket/slug, not by date/slug

class MediaFile(models.Model):
    """
    The base for media files; associated with a MediaBucket, as well
    as the articles in which it is used.
    
    Include authorship and licensing details, if relevant, in the ``license``
    field. If the file was created by one or more users, use the ``users`` m2m.
    """
    
    data = models.FileField(upload_to="by_date/%Y/%m/%d")
    
    name   = models.CharField(max_length=100)
    slug   = models.SlugField()
    bucket = models.ForeignKey(MediaBucket, related_name="files")
    
    users = models.ManyToManyField(UserProfile, related_name="media", blank=True)
    
    description = models.TextField(blank=True)
    license     = models.TextField(blank=True)
    
    pub_date = models.DateTimeField(blank=True, default=datetime.now)
    
    def credit(self):
        authors = self.users.order_by('user__last_name').all()
        return ', '.join(user.name for user in authors)
    
    def __unicode__(self):
        return "%s (in %s)" % (self.slug, self.bucket)
    
    def get_absolute_url(self):
        return self.data.url
    
    class Meta:
        unique_together = ("slug", "bucket")
    


class ImageFile(MediaFile):
    """
    An image file. Adds some extra functionality to MediaFile, relating to 
    resizing and cropping the image.
    """
    SHAPE_CHOICES = (
        ('t', 'tall'),
        ('w', 'wide'),
    )
    shape = models.CharField(max_length=1, choices=SHAPE_CHOICES)
    # TODO: implement ImageFile stuff
