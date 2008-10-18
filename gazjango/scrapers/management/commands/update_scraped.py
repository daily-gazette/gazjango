from django.core.management.base import LabelCommand
import gazjango.issues.models as issue_models

class Command(LabelCommand):
    """Updates scraped objects."""
    
    def update_bico(self):
        import gazjango.scrapers.bico
        gazjango.scrapers.bico.get_bico_news(override_cache=True)
    
    def update_tla(self):
        import gazjango.scrapers.tla
        gazjango.scrapers.tla.get_tla_links(override_cache=True)
    
    def update_events(self):
        issue_models.Event.objects.update()
    
    def update_menu(self):
        issue_models.Menu.objects.for_today(   ignore_cached=True)
        issue_models.Menu.objects.for_tomorrow(ignore_cached=True)
    
    def update_weather(self):
        issue_models.Weather.objects.for_today(   ignore_cached=True)
        issue_models.Weather.objects.for_tomorrow(ignore_cached=True)
    
    def handle_label(self, label, **options):
        lookup = {
            'bico':    self.update_bico,
            'tla':     self.update_tla,
            'events':  self.update_events,
            'menu':    self.update_menu,
            'weather': self.update_weather
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
    
