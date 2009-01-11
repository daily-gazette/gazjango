from django.shortcuts       import get_object_or_404, render_to_response
from django.template        import RequestContext

from gazjango.articles.models  import Section
from gazjango.reviews.models   import Establishment, Review
import settings

def reviews(request):
    'View for "establishment review" page.'
    
    establishments = Establishment.objects.order_by("establishment_type","name")    
    
    rc = RequestContext(request, { 
        'establishments': establishments,
        'GMAPS_API_KEY': settings.GMAPS_API_KEY,
        'TYPE_CHOICES': Establishment.TYPE_CHOICES,
    })
    return render_to_response('reviews/index.html', context_instance=rc)
