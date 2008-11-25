from django.core.cache import cache
import urllib2
try:
    from xml.etree import cElementTree as etree
except ImportError:
    from xml.etree import ElementTree as etree

CACHE_KEY = 'tla_links'

def get_tla_links(override_cache=False):
    cached = cache.get(CACHE_KEY)
    if cached and not override_cache:
        return cached
    else:
        try:
            links = get_tla_links_directly()
            cache.set(CACHE_KEY, links, 1 * 60 * 60 + 60)
            return links
        except urllib2.URLError:
            # TODO: log this error
            return []
        except SyntaxError:
            # etree is kind of silly in raising syntax errors, I feel
            # this usually means that the returned response was blank
            return []


def get_tla_links_directly():
    url = "http://www.text-link-ads.com/xml.php?inventory_key=N085BPUAZXJB74O3QZ06"
    feed = etree.parse(urllib2.urlopen(url))
    links = []
    
    for link in feed.findall("/Link"):
        before = link.find('BeforeText').text
        url = link.find('URL').text
        text = link.find('Text').text
        after = link.find('AfterText').text
        
        s = '%s <a href="%s">%s</a> %s' % (before, url, text, after)
        links.append(s)
    
    return links
