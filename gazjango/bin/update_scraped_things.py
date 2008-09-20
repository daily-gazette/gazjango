#!/usr/bin/env python

import sys, os
# doesn't work on windows
path = os.path.abspath(__file__).split(os.path.sep)
sys.path.append(os.path.sep.join(path[:-2]))
import settings

from django.core.management import setup_environ
setup_environ(settings)

from django.core.cache import cache
import gazjango.issues.models as issue_models

def update_bico():
    import gazjango.scrapers.bico
    gazjango.scrapers.bico.get_bico_news(override_cache=True)

def update_tla():
    import gazjango.scrapers.tla
    gazjango.scrapers.tla.get_tla_links(override_cache=True)

def update_events():
    issue_models.Event.objects.update()

def update_menu():
    issue_models.Menu.objects.for_today(   ignore_cached=True)
    issue_models.Menu.objects.for_tomorrow(ignore_cached=True)

def update_weather():
    issue_models.Weather.objects.for_today(   ignore_cached=True)
    issue_models.Weather.objects.for_tomorrow(ignore_cached=True)


def do_updates(keys):
    to_do = set()
    k = { 'bico':    update_bico,
          'tla':     update_tla,
          'events':  update_events,
          'menu':    update_menu,
          'weather': update_weather }
    
    if 'all' in keys:
        to_do.update(set(k.values()))
    else:
        for key, func in k.items():
            if key in keys:
                to_do.add(func)
    for func in to_do:
        func()

if __name__ == '__main__':
    import sys
    do_updates(sys.argv[1:])
