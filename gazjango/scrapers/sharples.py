import urllib2
from BeautifulSoup import BeautifulStoneSoup
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
    try:
        page = urllib2.urlopen(url)
    except urllib2.URLError:
        # TODO: log this error somehow
        message = "Sorry, it seems we're having some technical difficulties " \
                  "with figuring out the Sharples menu. Try checking the " \
                  "Dashboard or the Sharples website."
        return { 'closed': True, 'message': message }

    feed = BeautifulStoneSoup(page, selfClosingTags=['closed'])
    data = {}
    
    data['closed'] = feed.closed['value'] == "1"
    data['message'] = feed.message.string or ""
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
        meal = item.meal.string.strip()
        if meal:
            data[meal.lower()] = item.menu.string.strip()
    
    return data
