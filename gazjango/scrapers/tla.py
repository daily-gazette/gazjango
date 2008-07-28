from django.core.cache import cache
from xml.etree import cElementTree as etree
from urllib2   import urlopen

def get_tla_links():
    cached = cache.get('tla_links')
    if cached:
        return cached
    else:
        try:
            return update_tla_links()
        except URLError:
            return []


def update_tla_links():
    url = "http://www.text-link-ads.com/xml.php?inventory_key=N085BPUAZXJB74O3QZ06"
    feed = etree.parse(urlopen(url))
    links = []
    
    for link in feed.findall("/Link"):
        before = link.find('BeforeText').text
        url = link.find('URL').text
        text = link.find('Text').text
        after = link.find('AfterText').text
        
        s = '%s <a href="%s">%s</a> %s' % (before, url, text, after)
        links.append(s)
    
    cache.set('tla_links', links, 1 * 60 * 60)
    return links
