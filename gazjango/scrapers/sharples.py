from BeautifulSoup import BeautifulStoneSoup
from urllib2       import urlopen
from datetime      import date, timedelta

FEED_URL = "http://www.swarthmore.edu/dashboards/feeds/sharples.xml"
NUM_WEEKS = 4

def get_menu(url=FEED_URL, tomorrow=False, die_on_closed=False):
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
    
    If ``tomorrow`` is set, tries to figure out the menu for tomorrow.
    """
    
    feed = BeautifulStoneSoup(urlopen(url), selfClosingTags=['closed'])
    data = {}
    
    data['closed'] = feed.closed['value'] == "1"
    data['message'] = feed.message.string
    if data['closed'] and die_on_closed:
        return data
    
    week = feed.find("week", {'currentwk': '1'})
    
    if tomorrow:
        day_name = (date.today() + timedelta(days=1)).strftime("%A")
        if day_name == "Saturday":
            num = int(week['value']) + 1
            if num > NUM_WEEKS:
                num = 1
            week = feed.find("week", {'value': str(num)})
    else:
        day_name = date.today().strftime("%A")
    
    for item in week.find("day", {'value': day_name}).findAll("item"):
        data[item.meal.string.strip().lower()] = item.menu.string.strip()
    
    return data
