from datetime import date, timedelta
import feedparser
import re

RSS_URL = "http://calendar.swarthmore.edu/calendar/RSSSyndicator.aspx?category=" \
          "&location=&type=N&binary=N&keywords="

def scrape_events_feed(start=None, end=None):
    """
    Gets events from the College's RSS feed calendar.
    
    If `start` is passed, start at the given date; defaults to today.
    Note that this is not reliable for past dates.
    
    If `end` is passed, don't return any events after the specified date.
    """    
    start_date = start if start else date.today()
    # if we have a num, try a week; if that's not enough we'll add more later
    end_date = end if end else date.today() + timedelta(days=7)
    
    url = RSS_URL
    url += "&starting=%s" % start_date.strftime("%m/%d/%Y")
    url += "&ending=%s"   %   end_date.strftime("%m/%d/%Y")
    
    feed = feedparser.parse(url)
    events = []
    
    d = r'(?P<month%(s)s>\d{1,2})/(?P<day%(s)s>\d{1,2})/(?P<year%(s)s>\d{4})'
    reps = tuple(d % {'s': '_' + str(i)} for i in (1,2))
    title_pattern = re.compile(r'^(?P<name>.*)\s+\(%s(?: - %s)?\)$' % reps)
    
    for entry in feed.entries:
        match = re.match(title_pattern, entry.title.strip())
        if match:
            d = match.groupdict()
            result = {}
            
            result['name'] = d['name']
            result['link'] = entry.link
            
            ns = ('year', 'month', 'day')
            make_date = lambda d, s: date(*[int(d['%s_%s' % (n, s)]) for n in ns])
            
            result['start'] = make_date(d, 1)
            if 'year_2' in d and d['year_2']:
                result['end'] = make_date(d, '2')
            else:
                result['end'] = None
            
            events.append(result)
        else:
            # TODO: log this error somehow
            pass
    
    return events
