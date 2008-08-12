from xml.etree import cElementTree as etree
import urllib2
import datetime

# the National Weather Service provides us a nice xml feed with lots of weather data
# <3 the US government
FEED_URL = "http://www.weather.gov/forecasts/xml/sample_products/browser_interface/ndfdBrowserClientByDay.php?format=12+hourly&lat=%(lat)s&lon=%(lon)s&numDays=3&startDate=%(date)s"

SWAT_LAT_LONG = {'lat': '39.903959', 'lon': '-75.35398'}

class WeatherError(Exception):
    "Some kind of error in getting the weather."

class WeatherLoadError(WeatherError):
    "An error in loading the weather feed."

class WeatherParseError(WeatherError):
    "An error in parsing the weather feed."


def get_weather(date=None):
    """
    Gets weather from the National Weather Service and returns data
    in a dictionary, where keys are "today", "tonight", "tomorrow" and
    values are like "Mostly Clear. High of 86."
    """
    if date is None:
        date = datetime.date.today()
    
    reps = SWAT_LAT_LONG
    reps['date'] = date.strftime("%Y-%m-%d")
    url = FEED_URL % reps
    
    try:
        page = urllib2.urlopen(url)
    except urllib2.URLError:
        # TODO: log this error somehow
        raise WeatherLoadError("Couldn't load the feed.")
    
    feed = etree.parse(page)
    
    if feed.getroot().tag == "error":
        raise WeatherParseError("The feed returned an error.")
    
    results = {}
    params = feed.find("//parameters")
    
    weather_conditions = params.find("weather").findall("weather-conditions")
    # 0 is overnight (ie last night)
    results['today']    = weather_conditions[1].attrib['weather-summary']
    results['tonight']  = weather_conditions[2].attrib['weather-summary']
    results['tomorrow'] = weather_conditions[3].attrib['weather-summary']
    
    for temp in params.findall('temperature'):
        if temp.attrib['type'] == 'maximum':
            vals = ["High of %s." % val.text for val in temp.findall("value")]
            results['today']    += ". " + vals[0]
            results['tomorrow'] += ". " + vals[1]
        
        elif temp.attrib['type'] == 'minimum':
            vals = ["Low of %s." % val.text for val in temp.findall("value")]
            results['tonight'] += ". " + vals[1]
        
        else:
            s = "Unknown <temperature> tag type: %s." % temp.attrib['type']
            raise WeatherParseError(s)
    
    return results
