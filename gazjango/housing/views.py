from django.contrib.auth.decorators import login_required
from django.core.urlresolvers       import reverse
from django.http                    import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts               import render_to_response, get_object_or_404
from django.template                import RequestContext
from django.utils                   import simplejson as json

from gazjango.housing.models     import HousingListing
from gazjango.housing.forms      import SubmitHousingForm
from gazjango.misc.view_helpers  import get_user_profile

import datetime
import urllib
import settings

def list_housing(request):
    housing = HousingListing.published.order_by('-pub_date')
    profile = get_user_profile(request)
    
    newuser = True
    if profile:
        for listing in housing:
            if listing.student == profile:
                newuser = False
    
    if profile:
        needs_email = not request.user.email
        needs_name  = not request.user.get_full_name()
        if request.method == 'POST':
            form = SubmitHousingForm(request.POST, needs_email=needs_email, needs_name=needs_name)
            if form.is_valid():
                submission = form.save(commit=False)
                profile = get_user_profile(request)
                submission.student = profile
                submission.save()
                if needs_email:
                    profile.user.email = form.cleaned_data['email']
                if needs_name:
                    names = (form.cleaned_data['name'] + ' ').split(' ', 1)
                    profile.user.first_name, profile.user.last_name = names
                if needs_email or needs_name:
                    profile.user.save()
                    profile.save()
                form.save_m2m()
                return HttpResponseRedirect(reverse(list_housing))
        else:
            form = SubmitHousingForm(needs_email=needs_email,needs_name=needs_name)
    else:
        form = SubmitHousingForm(needs_email=False,needs_name=False)
    
    return render_to_response('listings/housing/list.html', {
        'housing': housing,
        'form': form,
        'person': profile,
        'newuser': newuser,
        'GMAPS_API_KEY': settings.GMAPS_API_KEY,
    }, context_instance=RequestContext(request))

def senior_success(request, template="listings/housing/success.html"):
    return render_to_response(template, {}, context_instance=RequestContext(request))
