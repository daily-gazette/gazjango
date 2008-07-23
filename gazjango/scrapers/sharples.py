from BeautifulSoup import BeautifulStoneSoup
from urllib2       import urlopen
from datetime      import date

FEED_URL = "http://www.swarthmore.edu/dashboards/feeds/sharples.xml"

def get_menu(url=FEED_URL, die_on_closed=False):
    """
    Builds a Sharples menu from ``url``, returning a dictionary like this:
    
    { 
        'closed': False, 
        'message': "",
        'lunch': "beef vegetable soup, potato leek, ...",
        'dinner': "flank steak, baked stuffed potatoes, ..."
    }
    
    Note that we still return the menu if Sharples is closed, unless
    ``die_on_closed`` is set.
    """
    
    feed = BeautifulStoneSoup(urlopen(url), selfClosingTags=['closed'])
    data = {}
    
    data['closed'] = feed.closed['value'] == "1"
    data['message'] = feed.message.string
    if data['closed'] and die_on_closed:
        return data
    
    day_name = date.today().strftime("%A")
    day = feed.find("week", {'currentwk': '1'}).find("day", {'value': day_name})
    
    for item in day("item"):
        data[item.meal.string.strip().lower()] = item.menu.string.strip()
    return data
