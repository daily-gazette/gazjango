from django.db import models
from gazjango.ads import managers

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
