from django.core.management.base import LabelCommand
from gazjango.blogroll.models import OutsideSite
from gazjango.issues.models   import Event, Menu, Weather

class Command(LabelCommand):
    """Updates scraped objects."""
    
    def update_bico(self):
        import gazjango.scrapers.bico
        gazjango.scrapers.bico.get_bico_news(override_cache=True)
    
    def update_events(self):
        Event.objects.update()
    
    def update_menu(self):
        Menu.objects.for_today(   ignore_cached=True)
        Menu.objects.for_tomorrow(ignore_cached=True)
    
    def update_weather(self):
        Weather.objects.for_today(   ignore_cached=True)
        Weather.objects.for_tomorrow(ignore_cached=True)
    
    def update_blogroll(self):
        OutsideSite.objects.update_all()
    
    def handle_label(self, label, **options):
        lookup = {
            'bico':     self.update_bico,
            'events':   self.update_events,
            'menu':     self.update_menu,
            'weather':  self.update_weather,
            'blogroll': self.update_blogroll,
        }
        if label == 'all':
            for name, f in lookup.items():
                print "updating", name
                f()
        else:
            if label in lookup:
                print "updating", label
                lookup[label]()
            else:
                raise NotImplementedError()
    
