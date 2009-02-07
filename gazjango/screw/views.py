from django.contrib.auth.decorators import login_required
from django.core.urlresolvers       import reverse
from django.http                    import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts               import render_to_response, get_object_or_404
from django.template                import RequestContext

from gazjango.screw.models      import ScrewListing
from gazjango.screw.forms       import SubmitScreweeForm
from gazjango.misc.view_helpers import get_user_profile

import datetime

@login_required
def list_screws(request):
    books = ScrewListing.published.filter(screwed_at=None).order_by('-pub_date')
    profile = get_user_profile(request)
    
    needs_email = not request.user.email
    if request.method == 'POST':
        form = SubmitScreweeForm(request.POST, needs_email=needs_email)
        if form.is_valid():
            screw = form.save(commit=False)
            profile = get_user_profile(request)
            screw.screwee = profile
            screw.save()
            if needs_email:
                profile.user.email = form.cleaned_data['email']
                profile.save()
            form.save_m2m()
            # return HttpResponseRedirect(reverse(book_success))
            return HttpResponseRedirect(reverse(list_books))
    else:
        form = SubmitBookForm(needs_email=needs_email)
    
    return render_to_response('listings/screw/listings.html', {
        'screws': screws,
        'screwee': profile,
        'form': form,
    }, context_instance=RequestContext(request))

def mark_as_screwed(request, slug):
    screw = get_object_or_404(ScrewListing, slug=slug)
    profile = get_user_profile(request)
    
    if profile and profile == screw.screwee:
        screw.screwed_at = datetime.datetime.now()
        screw.save()
        if request.is_ajax():
            return HttpResponse('success')
        else:
            return HttpResponseRedirect(reverse(list_screws))
    else:
        if request.is_ajax():
            return 'denied'
        else:
            raise Http404

def screw_success(request, template="listings/screw/success.html"):
    return render_to_response(template, {}, context_instance=RequestContext(request))
