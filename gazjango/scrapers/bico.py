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
DEFAULT_ORDER = ('news', 'features', 'sports')

def get_bico_news(order=DEFAULT_ORDER):
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
    
    key = 'bico_' + '_'.join(order)
    cached = cache.get(key)
    
    if cached:
        return cached
    else:
        results = get_bico_news_directly(order)
        cache.set(key, results, 13 * 60 * 60)
        return results


def get_bico_news_directly(order=DEFAULT_ORDER):
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
            feed, next = feeds[cat]
        else:
            feed = feedparser.parse(BASE_URL + CATEGORIES[cat])
            next = 0
            feeds[cat] = (feed, next)
        
        entry = feed.entries[next]
        
        # awesomely enough, BiCo doesn't really set their authors; they
        # just have the first line "<p><strong>By Joe Schmoe</strong></p>"
        
        content = entry.content[0].value
        regex = r'^\s*<p>\s*<strong>\s*By\s+([-\w\s]+)\s*</strong>'
        match = re.match(regex, content, re.IGNORECASE)
        if match:
            author = match.group(1)
        else:
            author = "the Bi-Co News"
        
        result.append({
            'headline': entry.title,
            'link': entry.link,
            'author': author
        })
    
    return result
