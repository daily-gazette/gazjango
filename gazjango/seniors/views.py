from django.contrib.auth.decorators import login_required
from django.core.urlresolvers       import reverse
from django.http                    import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts               import render_to_response, get_object_or_404
from django.template                import RequestContext
from django.utils                   import simplejson as json

from gazjango.senior.models     import SeniorListing
from gazjango.senior.forms      import SubmitSeniorForm
from gazjango.misc.view_helpers import get_user_profile

import datetime
import urllib
import settings

@login_required
def list_seniors(request):
    seniors = SeniorListing.published.order_by('-pub_date')
    profile = get_user_profile(request)
    
    needs_email = not request.user.email
    if request.method == 'POST':
        form = SubmitSeniorForm(request.POST, needs_email=needs_email)
        if form.is_valid():
            submission = form.save(commit=False)
            profile = get_user_profile(request)
            submission.senior = profile
            submission.save()
            if needs_email:
                profile.user.email = form.cleaned_data['email']
                profile.save()
            form.save_m2m()
            return HttpResponseRedirect(reverse(list_seniors))
    else:
        form = SubmitSeniorForm(needs_email=needs_email)
    
    return render_to_response('listings/seniors/list.html', {
        'seniors': seniors,
        'form': form,
        'user': profile,
        'GMAPS_API_KEY': settings.GMAPS_API_KEY,
        'locations': locations,
        'loc_dict': dict(reversed(x) for x in locations),
    }, context_instance=RequestContext(request))

def senior_success(request, template="listings/seniors/success.html"):
    return render_to_response(template, {}, context_instance=RequestContext(request))
