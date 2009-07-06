import urllib2
import feedparser
import re

BASE_URL = "http://www.biconews.com/?feed=rss2&cat="
CATEGORIES = {
    'news': '1',
    'features': '3',
    'arts': '4',
    'sports': '5',
    'opinion': '6',
    'last-word': '7'
}
DEFAULT_ORDER = ('news', 'features', 'arts', 'sports')
AUTHOR_REGEX = re.compile(r'^\s*<p>\s*<strong>\s*By\s+([-\w\s\']+)\s*</strong>', re.I)


def cache_item_name(order=DEFAULT_ORDER):
    """Returns the key that will be used for the cache."""
    return 'bico_' + '_'.join(order)


def get_bico_news(order=DEFAULT_ORDER, override_cache=False):
    """
    Caches the BiCo News feed.
    
    Feed results for a given order are stored in the cache like this:
    
    bico_news_features_sports => [
        {'author': ..., 'headline': ..., 'link': ...},
        {'author': ..., 'headline': ..., 'link': ...},
        {'author': ..., 'headline': ..., 'link': ...}
    ]
    """
    # so we can use the main file w/o django...
    from django.core.cache import cache
    
    key = cache_item_name(order)
    cached = cache.get(key)
    
    if cached and not override_cache:
        return cached
    else:
        try:
            results = get_bico_news_directly(order)
            cache.set(key, results, 13 * 60 * 60)
            return results
        except urllib2.URLError:
            # TODO: log this somehow
            cache.set(key, "error", 1 * 60 * 60)
            return "error"


def get_bico_news_directly(order=DEFAULT_ORDER):
    """Gets the bico news, not doing any caching or anything."""
    # NOTE: if we can assume that the main feed will always contain
    #       enough entries of each type, we could use that, and only
    #       have to read / parse one feed. however, this is often not
    #       true, as Last Word articles, true to their name, generally
    #       seem to be uploaded last, so the main feed tends to be
    #       mostly Last Words.
    
    feeds = {}
    result = []
    
    for cat in order:
        if cat in feeds:
            feed, index = feeds[cat]
            index += 1
            feeds[cat] = (feed, index)
        else:
            try:
                url = urllib2.urlopen(BASE_URL + CATEGORIES[cat])
            except urllib2.URLError, e:
                raise e
            
            feed = feedparser.parse(url)
            index = 0
            feeds[cat] = (feed, index)
        
        try:
            entry = feed.entries[index]
        except IndexError:
            continue
        
        # awesomely enough, BiCo doesn't really set their authors; they
        # just have the first line "<p><strong>By Joe Schmoe</strong></p>"
        
        content = entry.content[0].value
        
        match = re.match(AUTHOR_REGEX, content)
        if match:
            author = match.group(1)
        else:
            # TODO: log this error
            author = "the Bi-Co News"
        
        result.append({
            'headline': entry.title,
            'link': entry.link,
            'author': author
        })
    
    return result
