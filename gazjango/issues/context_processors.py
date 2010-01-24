from gazjango.issues.models import Weather, WeatherJoke
from gazjango.misc.helpers import cache

@cache(60*60)
def weather_joke(request):
    return {
        'weather': Weather.objects.for_today(),
        'weather_joke': WeatherJoke.objects.latest(),
    }
