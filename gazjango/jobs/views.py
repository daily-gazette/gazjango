from django.core.urlresolvers import reverse
from django.http              import HttpResponseRedirect
from django.template          import RequestContext
from django.shortcuts         import render_to_response, get_object_or_404
from gazjango.jobs.models     import JobListing
from gazjango.jobs.forms      import SubmitJobForm
from gazjango.announcements.models import Poster

import datetime

def job_details(request, slug, template="listings/jobs/details.html"):
    job = get_object_or_404(JobListing, slug=slug)
    data = {
        'job': job,
        'other_jobs': JobListing.unfilled.order_by('-pub_date')[:3],
        'poster': Poster.published.get_running(),
    }
    rc = RequestContext(request)
    return render_to_response(template, data, context_instance=rc)


def list_jobs(request, template="listings/jobs/list.html"):
    lim = datetime.date.today() - datetime.timedelta(days=60)
    jobs = JobListing.unfilled.filter(pub_date__gte=lim).order_by('-pub_date')

    rc = RequestContext(request)
    return render_to_response(template, {'jobs': jobs}, context_instance=rc)


def submit_job(request, template="listings/jobs/submit.html"):
    if request.method == 'POST':
        form = SubmitJobForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse(job_success))
    else:
        form = SubmitJobForm()
    
    data = { 'form': form , 'poster': Poster.published.get_running(),}
    rc = RequestContext(request)
    return render_to_response(template, data, context_instance=rc)

def job_success(request, template="listings/jobs/success.html"):
    return render_to_response(template, {}, context_instance=RequestContext(request))
