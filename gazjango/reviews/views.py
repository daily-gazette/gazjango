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
            request.session['submitted_name'] = form.cleaned_data['name']
            return HttpResponseRedirect(reverse(reviews))
    else:
        form = SubmitEstablishmentForm()
    
    establishments = Establishment.published.order_by("establishment_type", "name")    
    
    submitted_name = request.session.get('submitted_name', None)
    if submitted_name:
        del request.session['submitted_name']
    
    rc = RequestContext(request, { 
        'establishments': establishments,
        'GMAPS_API_KEY': settings.GMAPS_API_KEY,
        'TYPE_CHOICES': Establishment.TYPE_CHOICES,
        'submit_form': form,
        'submitted_name': submitted_name,
    })
    return render_to_response('reviews/index.html', context_instance=rc)
