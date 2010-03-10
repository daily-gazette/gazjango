from django.db import models
from django.utils.safestring import mark_safe

from gazjango.ads import managers
from gazjango.media.models import MediaFile, ImageFile, OutsideMedia

import datetime

class TextLinkAd(models.Model):
    SOURCES = [('t', 'TLA'), ('l', 'LinkWorth'), ('c', 'LiveCustomer')]
    source = models.CharField(blank=True, max_length=1, choices=SOURCES)
    
    link = models.URLField(blank=True, verify_exists=False)
    text = models.CharField(blank=True, max_length=100)
    override = models.CharField(blank=True, max_length=200,
        help_text="If set, this will be shown in the HTML rather than the default plain link.")
    
    objects = managers.TextLinkAdsManager()
    tla = managers.TLAAdsManager()
    linkworth = managers.LinkWorthAdsManager()
    livecustomer = managers.LiveCustomerAdsManager()
    
    class Meta:
        ordering = ['source', 'text']
    
    def render(self):
        if self.override:
            return self.override
        else:
            return "<a href='%s'>%s</a>" % (self.link, self.text)
    
    def __unicode__(self):
        return u"%s [%s]" % (self.text, self.get_source_display())
    


class BannerAd(models.Model):
    SPACE_CHOICES = [('f', "Front Page"), ('t', "Article Top Banner"), ('s', "Article Side Banner")]
    space = models.CharField(max_length=1, choices=SPACE_CHOICES)
    
    publisher = models.CharField(max_length=100)
    link = models.URLField(blank=True, verify_exists=True)
    description = models.TextField(blank=True)
    
    TYPE_CHOICES = [('i', "Image"), ('o', "Outside Media")]
    render_type = models.CharField(max_length=1, choices=TYPE_CHOICES)
    image = models.ForeignKey(ImageFile, null=True, blank=True)
    outside = models.ForeignKey(OutsideMedia, null=True, blank=True)
    
    @property
    def media(self):
        if self.render_type == 'i':
            return self.image
        elif self.render_type == 'o':
            return self.outside
    
    date_start = models.DateField(default=datetime.date.today,
        help_text="First day for the ad to run.")
    date_end   = models.DateField(default=datetime.date.today,
        help_text="Last day for the ad to run.")
    
    priority = models.FloatField(default=1,
        help_text="The priority with which this ad should appear; an ad of priority "
                  "2 will show up twice as often as one with priority 1. An ad with "
                  "a priority of 0 will only be picked if there are no ads with "
                  "nonzero priority.")
    
    objects = managers.BannerAdsManager()
    front = managers.FrontPageAdsManager()
    article_top = managers.ArticleTopBannerAdsManager()
    article_side = managers.ArticleSideBannerAdsManager()
    
    def linked_publisher(self):
        if self.link:
            s = '<a href="%s">%s</a>' % (self.link, self.publisher)
        else:
            s = self.publisher
        return mark_safe(s)

    def display(self):
        if self.render_type == 'i':
            s = '<img src="%(url)s" alt="%(name)s" title="%(name)s" />' % {
                'url': getattr(self.image, 'bannerad%s' % self.space).url,
                'name': self.publisher.replace('"', '\\"')
            }
            if self.link:
                s = '<a href="%s">%s</a>' % (self.link, s)
        elif self.render_type == 'o':
            s = self.outside.data
        else:
            raise ValueError("invalid content type for this ad's media")
        return mark_safe(s) # make sure this gets rendered as raw html in templates
    
    def __unicode__(self):
        return "%s [%s; %s]" % (self.publisher, self.date_start, self.get_space_display())
    
