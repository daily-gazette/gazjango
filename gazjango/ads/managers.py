from django.db import models

import urllib2
try:
    from xml.etree import cElementTree as etree
except ImportError:
    from xml.etree import ElementTree as etree


class TextLinkAdsManager(models.Manager):
    source = None
    
    def get_query_set(self):
        orig = super(TextLinkAdsManager, self).get_query_set()
        return orig.filter(source=self.source) if self.source else orig
    
    def update(self):
        "Replace the ad objects for this source with ones from the web feed."
        try:
            ads = self._get_ads()
            if not ads:
                return False
                
            # we have some, so delete the old objects and replace them
            self.all().delete()
            for ad in ads:
                a = self.create(
                    source=self.source,
                    link=ad['url'],
                    text=ad['text'],
                )
                if ad['before'] or ad['after']:
                    a.override = "%(before)s<a href='%(url)s'>%(text)s</a>%(after)s" % ad
                    a.save()
            return True
        except urllib2.URLError:
            return False
        except SyntaxError: # happens from etree if the feed is blank (?)
            return False
    
    def _get_ads(self, url=None):
        """
        Gets the ads from the web feed. Subclasses supporting this operation should
        override this function to return a list of dictionaries like
        
        { 'url': 'http://example.com', 'text': 'Some Ad',
          'before': '', 'after': '' }
        """
        raise NotImplemented
    

class TLAAdsManager(TextLinkAdsManager):
    source = 't'
    
    SOURCE_URL = "http://www.text-link-ads.com/xml.php?inventory_key=N085BPUAZXJB74O3QZ06"
    def _get_ads(self, url=None):
        feed = etree.parse(urllib2.urlopen(url or self.SOURCE_URL))
        process = lambda link: {
            'before': link.find('BeforeText').text,
            'url': link.find('URL').text,
            'text': link.find('Text').text,
            'after': link.find('AfterText').text,
        }
        return [process(link) for link in feed.findall("/Link")]
    

class LinkWorthAdsManager(TextLinkAdsManager):
    source = 'l'
    
    SOURCE_URL = "http://feeds.plawr.com/?0d478e5d5257f22428aa8e72b2e2d19e831"
    def _get_ads(self, url=None):
        feed = etree.parse(urllib2.urlopen(url or self.SOURCE_URL))
        process = lambda item: {
            'before': '',
            'url': item.find('link').text,
            'text': item.find('title').text,
            'after': (lambda s: '- %s' % s if s else '')(item.find('description').text),
        }
        return [process(item) for item in feed.findall('/channel/item')]
    

class LiveCustomerAdsManager(TextLinkAdsManager):
    source = 'c'
    
    # no web feed for this one, it's manual
    def update(self):
        return True
