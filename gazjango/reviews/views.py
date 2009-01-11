from django.core.urlresolvers import reverse
from django.http              import HttpResponseRedirect
from django.shortcuts         import get_object_or_404, render_to_response
from django.template          import RequestContext

from gazjango.articles.models import Section
from gazjango.reviews.models  import Establishment, Review
from gazjango.reviews.forms   import SubmitEstablishmentForm
import urllib
import settings

def reviews(request):
    'View for "establishment review" page.'
    
    if request.method == 'POST':
        form = SubmitEstablishmentForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse(reviews) + 
                        '?name=' + urllib.quote_plus(form.cleaned_data['name']))
    else:
        form = SubmitEstablishmentForm()
    
    establishments = Establishment.published.order_by("establishment_type", "name")    
    
    rc = RequestContext(request, { 
        'establishments': establishments,
        'GMAPS_API_KEY': settings.GMAPS_API_KEY,
        'TYPE_CHOICES': Establishment.TYPE_CHOICES,
        'submit_form': form,
        'submitted_name': request.GET.get('name', None),
    })
    return render_to_response('reviews/index.html', context_instance=rc)
