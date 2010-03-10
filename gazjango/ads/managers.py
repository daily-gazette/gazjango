from django.db import models, IntegrityError
from django.conf import settings

import datetime
import random
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



class BannerAdsManager(models.Manager):
    space = None
    def get_query_set(self):
        orig = super(BannerAdsManager, self).get_query_set()
        return orig.filter(space=self.space) if self.space else orig
    
    def create(self, *args, **kwargs):
        if self.space:
            kwargs.setdefault('space', self.space)
            if kwargs['space'] != self.space:
                s = "manager is for space '%s'; can't make for requested space '%s'"
                raise ValueError(s % (self.space, kwargs['space']))
        else:
            if not kwargs.get('space', None):
                raise IntegrityError('space cannot be null')
        return super(BannerAdsManager, self).create(*args, **kwargs)
    
    def get_running(self, date=None):
        if not date:
            date = datetime.date.today()
        return self.filter(date_start__lte=date, date_end__gte=date)
    
    def pick(self, date=None, allow_zero_priority=True):
        "Pick an ad running at `date`/now according to their priorities."
        # get the candidates and their weights
        candidates = self.get_running(date=date)
        nonzero_priority = candidates.exclude(priority=0)
        zero_priority = candidates.filter(priority=0)
        
        # choose a "priority index" and go to it in the cand list
        total_priority = sum(cand.priority for cand in nonzero_priority)
        if total_priority == 0:
            if not allow_zero_priority:
                return None
            try:
                return random.choice(zero_priority)
            except IndexError:
                return None
        
        pri_left = random.random() * total_priority # in [0, total_priority)
        for cand in candidates:
            if cand.priority >= pri_left:
                return cand
            pri_left -= cand.priority
    

class FrontPageAdsManager(BannerAdsManager):
    space = 'f'

class ArticleTopBannerAdsManager(BannerAdsManager):
    space = 't'

class ArticleSideBannerAdsManager(BannerAdsManager):
    space = 's'
