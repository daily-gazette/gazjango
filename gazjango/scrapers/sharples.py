from BeautifulSoup import BeautifulStoneSoup
from urllib2       import urlopen
from datetime      import date

FEED_URL = "http://www.swarthmore.edu/dashboards/feeds/sharples.xml"

def get_menu(ignore_closed=False):
    feed = BeautifulStoneSoup(urlopen(FEED_URL), selfClosingTags=['closed'])
    
    if feed.closed['value'] == '1' and not ignore_closed:
        return { 'closed': True, 'message': feed.message.string }
    
    day_name = date.today().strftime("%A")
    day = feed.find("week", {'currentwk': '1'}).find("day", {'value': day_name})
    
    meals = { 'closed': False }
    for item in day("item"):
        meals[item.meal.string.strip().lower()] = item.menu.string.strip()
    return meals
