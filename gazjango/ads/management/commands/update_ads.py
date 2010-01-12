from django.core.management.base import LabelCommand
from gazjango.ads.models import TextLinkAd

class Command(LabelCommand):
    def handle(self, *labels, **options):
        return super(Command, self).handle(*(labels or ['all']), **options)
    
    def handle_label(self, label, **options):
        if label == 'all':
            self.handle_label('tla', **options)
            self.handle_label('linkworth', **options)
            self.handle_label('livecustomer', **options)
        else:
            print "updating %s ..." % label,
            res = getattr(TextLinkAd, label).update()
            print "done" if res else "failed :("
    
