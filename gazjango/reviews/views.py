from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers           import reverse
from django.http                        import HttpResponse, HttpResponseRedirect
from django.shortcuts                   import get_object_or_404, render_to_response
from django.template                    import RequestContext
from django.utils                       import simplejson as json

from gazjango.articles.models    import Section
from gazjango.misc.helpers       import get_static_path
from gazjango.misc.view_helpers  import get_user_profile
from gazjango.reviews.directions import TRAIN_STATIONS
from gazjango.reviews.models     import Establishment, Review
from gazjango.reviews.forms      import SubmitEstablishmentForm, SubmitReviewForm
from gazjango.tagging.models     import Tag

import urllib
import settings

def reviews(request):
    'View for "establishment review" page.'
    
    establishments = Establishment.published.all()
    
    ct = ContentType.objects.get_for_model(Establishment)
    tags = Tag.objects.filter(group__content_types=ct)
    
    submitted_name = request.session.get('submitted_name', None)
    if submitted_name:
        del request.session['submitted_name']
    
    type_icons = [ (
        short,
        get_static_path('images', 'reviews/map-markers/%s.png' % short),
        get_static_path('images', 'reviews/map-markers/%s-shadow.png' % short)
    ) for short, long in Establishment.TYPE_CHOICES ]	
    
    topcityfood   = None
    toplocalfood  = None
    toplocalhotel = None
    
    for establishment in establishments.order_by():
        if establishment.establishment_type == 'r':
            if establishment.city == 'Swarthmore':
                if toplocalfood == None:
                    toplocalfood = establishment
                else:
                    if establishment.avg_rating() > toplocalfood.avg_rating():
                        toplocalfood = establishment
            elif establishment.city == 'Philadelphia':
                if topcityfood == None:
                    topcityfood = establishment
                else:
                    if establishment.avg_rating() > topcityfood.avg_rating():
                        topcityfood = establishment
        elif establishment.establishment_type == 'h':
            if toplocalhotel == None:
                toplocalhotel = establishment
            else:
                if establishment.avg_rating() > toplocalhotel.avg_rating():
                    toplocalhotel = establishment
                        
    locations = list(enumerate(establishments.
                   values_list('city', flat=True).order_by('city').distinct()))
    
    rc = RequestContext(request, { 
        'establishments': establishments.order_by(), # sorted client-side anyway
        'GMAPS_API_KEY': settings.GMAPS_API_KEY,
        'TYPE_CHOICES': Establishment.TYPE_CHOICES,
        'icons': type_icons,
        'submitted_name': submitted_name,
        'tags': tags,
        'locations': locations,
        'loc_dict': dict(reversed(x) for x in locations),
        'topcityfood': topcityfood,
        'toplocalfood': toplocalfood,
        'toplocalhotel': toplocalhotel, 
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
    estab = get_object_or_404(Establishment, slug=slug)
    user = get_user_profile(request)
    
    if request.method == 'POST':
        form = SubmitReviewForm(request.POST)
        if form.is_valid():
            try:
                review = estab.reviews.get(reviewer=user)
            except Review.DoesNotExist:
                review = Review(establishment=estab, reviewer=user)
            review.cost = form.cleaned_data['cost']
            review.rating = form.cleaned_data['rating']
            review.text = form.cleaned_data['text']
            review.save()
            return HttpResponseRedirect(reverse(establishment, 
                                                kwargs={'slug': slug}))
    else:
        try:
            review = estab.reviews.get(reviewer=user)
            form = SubmitReviewForm(review.__dict__)
        except Review.DoesNotExist:
            form = SubmitReviewForm()
    
    return render_to_response('reviews/establishment.html', {
        'establishment': estab,
        'reviews': estab.reviews.exclude(reviewer=user),
        'form': form,
    }, context_instance=RequestContext(request))

def list_trains(request):
    return HttpResponse(json.dumps(TRAIN_STATIONS.values()))
