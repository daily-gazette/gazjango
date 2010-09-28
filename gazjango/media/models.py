import datetime
import re

from django.db                   import models
from django.db.models            import signals

from gazjango.accounts.models import UserProfile
from gazjango.misc.helpers    import set_default_slug

from imagekit.models import ImageModel, ImageModelBase

class MediaBucket(models.Model):
    """
    A bucket containing media files related in some way.
    
    Probably, we want to limit the total number of buckets: make one for
    generic catch-alls, one for reusable pictures of buildings, one for
    generic reusables, etc.
    """
    
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    
    def __unicode__(self):
        return self.slug
    
_bucket_slugger = set_default_slug(lambda bucket: bucket.name)
signals.pre_save.connect(_bucket_slugger, sender=MediaBucket)


class BaseFile(models.Model):
    """
    The abstract base for media files; deals with most of the relevant metadata.
    """
    name = models.CharField(max_length=100)
    slug = models.SlugField()
    bucket = models.ForeignKey(MediaBucket, related_name="%(class)ss")
    
    author_name = models.CharField(max_length=100, blank=True,
        help_text="Who made this file -- overrides users, below. "
                  "Use if it was by someone who doesn't have an account.")
    users = models.ManyToManyField(UserProfile, related_name="%(class)s_set", blank=True)
    
    LICENSE_CHOICES = (
        ('g', 'Created by the Gazette'),
        ('c', 'Creative Commons'),
        ('f', 'Free for Public Use'),
        ('p', 'Specific permission from the creator'),
        ('o', 'Other (note in description)'),
    )
    license_type = models.CharField(max_length=1, blank=False,
                        choices=LICENSE_CHOICES, default='g',
                        help_text="Why is it okay for us to use this file?")
    source_url = models.URLField(blank=True, verify_exists=False)
    
    description = models.TextField(blank=True)
    pub_date = models.DateTimeField(blank=True, default=datetime.datetime.now)
    
    def credit(self):
        if self.author_name:
            return self.author_name
        else:
            return ', '.join(
                '%s %s' % names for names in
                self.users.order_by('user__last_name')
                          .values_list('user__first_name', 'user__last_name')
            )
    
    def __unicode__(self):
        return "%s/%s" % (self.bucket.slug, self.slug)
    
    class Meta:
        unique_together = ('slug', 'bucket')
        abstract = True
        ordering = ('-pub_date',)
    


class MediaFile(BaseFile):
    """
    A specific representation of a generic media file.
    
    All BaseFile subclasses *except* ImageFile should probably
    inherit from this.
    """
    data = models.FileField(upload_to="by_date/%Y/%m/%d")
    
    def get_absolute_url(self):
        return self.data.url
    


class ImageFile(BaseFile, ImageModel):
    """
    An image file. Adds a bunch of resizing stuff, from imagekit.
    """
    # default inheritance doesn't get the metaclass, since it's second
    __metaclass__ = ImageModelBase
    
    data = models.ImageField(upload_to="by_date/%Y/%m/%d")
    
    front_is_tall = models.BooleanField(default=False)
    """
    def update_front_is_tall(self):
        img = self._front_data or self.data
        if img:
            self.front_is_tall = img.height > img.width
    """
    
    # optional explicit cropping / resizings
    _front_data = models.ImageField(upload_to="by_date/%Y/%m/%d", blank=True,
        help_text="A version of this file to show on the frontpage. Should be 350px wide"
                  "and 120-200px tall, or 320px tall and 190-250px wide, for top stories."
                  "Mid stories can be a little smaller, 280x125 or 90x155."
    )
    _issue_data = models.ImageField(upload_to="by_date/%Y/%m/%d", blank=True,
        help_text="A version of this file to show in the issue, if it's the top story. "
                  "Should be 192x192 pixels. Note that although this can look okay in the "
                  "issue if it's not exactly square, it'll look weird if the article is "
                  "a special to show up on the bar on the front page."
    )
    _thumb_data = models.ImageField(upload_to="by_date/%Y/%m/%d", blank=True,
        help_text="A version of this file to show up at the bottom of the page, for top "
                  "stories only. Should be about 50x80."
    )
    
    
    class IKOptions:
        spec_module = 'gazjango.media.image_specs'
        cache_dir = 'resized'
        image_field = 'data'
        admin_thumbnail_spec = 'adminthumb'
    
    # NOTE: ImageFile inherits from both BaseMediaFile and ImageModel, 
    #       and each of these has a Meta class. this might be bad, 
    #       but ImageModel.Meta only sets abstract=True. if this
    #       changes in the future, some care might be required.
    class Meta(BaseFile.Meta, ImageModel.Meta):
        pass
    
    def get_front_image(self, top=True):
        if self._front_data:
            return self._front_data
        elif self.front_is_tall:
            return self.toptallfront if top else self.midtallfront
        else:
            return self.topwidefront if top else self.midwidefront
    
    top_front = property(get_front_image)
    mid_front = property(lambda self: self.get_front_image(top=False))
    poster    = property(lambda self: self.poster) # FIXME - some crazy shit here
    
    issue = property(lambda self: self._issue_data or self.issueimage)
    thumb = property(lambda self: self._thumb_data or self.thumbnail)
    
    def get_absolute_url(self):
        # TODO: change get_absolute_url to a default "display" spec
        return self.data.url
    
    def front_tall_or_wide(self):
        return "tall" if self.front_is_tall else "wide"
    


flickr_id = re.compile(r'^(?:http://)?(?:www\.)?flickr.com/photos/[^/]+/(\d+)/')

def get_from_flickr(url, name, user, bucket, size='Large'):
    from gazjango.scrapers import flickr
    import os, os.path
    import time
    from urllib import urlretrieve
    from django.conf import settings
    from django.template.defaultfilters import slugify

    flickr.API_KEY = settings.FLICKR_API
    flickr.API_SECRET = settings.FLICKR_SECRET

    m = flickr_id.match(url)
    if m:
        id = m.group(1)
    elif url.isdigit():
        id = url
    else:
        raise ValueError("confusing url '%s'" % url)

    p = flickr.Photo(id)
    size_url = p.getURL(size=size, urlType='source')

    if 'flickr.com' not in url:
        url = p.getURL(size=size, urlType='url')

    dir = time.strftime("by_date/%Y/%m/%d/")
    os_dir = os.path.join(settings.MEDIA_ROOT, dir)

    if not os.path.exists(os_dir):
        os.makedirs(os_dir)
    elif not os.path.isdir(os_dir):
        raise IOError("%s exists, but isn't a directory!" % os_dir)

    filename = size_url.split('/')[-1]

    urlretrieve(size_url, os.path.join(os_dir, filename))

    image = ImageFile.objects.create(
            data=os.path.join(dir, filename),
            name=name,
            slug=slugify(name),
            bucket=bucket,
            source_url=url,
    )
    image.users = [user]
    return image



# _update_front_is_tall = lambda sender, instance, **kwargs: instance.update_front_is_tall()
# signals.pre_save.connect(_update_front_is_tall, sender=ImageFile)

class OutsideMedia(BaseFile):
    """
    A media object to use for arbitrary things not connected to a FileField
    at all. For, say, embedding YouTube videos or whatnot.
    """
    data = models.TextField(blank=True,
        help_text='The HTML to insert the object. For a YouTube video or whatnot, '
                  'you probably want to copy this from the "embed" link. For '
                  'articles, it should be about 650px wide.')


MEDIA_CLASSES = [MediaFile, ImageFile, OutsideMedia]
_name_slugger = set_default_slug(lambda obj: obj.name)
for media_class in MEDIA_CLASSES:
    signals.pre_save.connect(_name_slugger, sender=media_class)
