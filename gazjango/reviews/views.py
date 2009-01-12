from django.core.urlresolvers import reverse
from django.http              import HttpResponseRedirect
from django.shortcuts         import get_object_or_404, render_to_response
from django.template          import RequestContext

from gazjango.articles.models             import Section
from gazjango.misc.helpers                import get_static_path
from gazjango.reviews.models              import Establishment, Review
from gazjango.reviews.forms               import SubmitEstablishmentForm
from gazjango.tagging.models              import Tag
from django.contrib.contenttypes.models   import ContentType

import urllib
import settings

def reviews(request):
    'View for "establishment review" page.'
    
    establishments = Establishment.published.order_by("establishment_type", "name")  
    ct = ContentType.objects.get_for_model(Establishment)  
    tags = Tag.objects.filter(group__content_type=ct)
    
    submitted_name = request.session.get('submitted_name', None)
    if submitted_name:
        del request.session['submitted_name']
    
    type_icons = [ (
        short,
        get_static_path('images', 'reviews/map-markers/%s.png' % short),
        get_static_path('images', 'reviews/map-markers/%s-shadow.png' % short)
    ) for short, long in Establishment.TYPE_CHOICES ]
    
    locations = list(enumerate(establishments.
                   values_list('city', flat=True).order_by('city').distinct()))
    
    rc = RequestContext(request, { 
        'establishments': establishments,
        'GMAPS_API_KEY': settings.GMAPS_API_KEY,
        'TYPE_CHOICES': Establishment.TYPE_CHOICES,
        'icons': type_icons,
        'submitted_name': submitted_name,
        'tags': tags,
        'locations': locations,
    })
    return render_to_response('reviews/index.html', context_instance=rc)

def submit_review(request):
    if request.method == 'POST':
        form = SubmitEstablishmentForm(request.POST)
        if form.is_valid():
            form.save()
            request.session['submitted_name'] = form.cleaned_data['name']
            return HttpResponseRedirect(reverse(reviews))
    else:
        form = SubmitEstablishmentForm()
    
    rc = RequestContext(request, { 'form': form })
    return render_to_response('reviews/submit.html', context_instance=rc)


def establishment(request, slug):
    'View for "establishment" pages.'
    
    establishment = get_object_or_404(Establishment, slug=slug)
    
    rc = RequestContext(request, { 'establishment': establishment })
    return render_to_response('reviews/establishment.html', context_instance=rc)
