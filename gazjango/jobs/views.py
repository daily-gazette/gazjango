from django.core.urlresolvers import reverse
from django.http              import HttpResponseRedirect
from django.template          import RequestContext
from django.shortcuts         import render_to_response, get_object_or_404
from gazjango.jobs.models     import JobListing
from gazjango.jobs.forms      import SubmitJobForm

def job_details(request, slug, template="listings/jobs/details.html"):
    job = get_object_or_404(JobListing, slug=slug)
    data = {
        'job': job,
        'other_jobs': JobListing.unfilled.order_by('-pub_date')[:3]
    }
    rc = RequestContext(request)
    return render_to_response(template, data, context_instance=rc)


def list_jobs(request, options="", default_limit=10, template="listings/jobs/list.html"):
    opts = options.split("/")
    opts = [(opt[:-1] if opt.endswith("/") else opt).lower() for opt in opts]
    
    conditions = {}
    for opt in opts:
        if opt in ('paid', 'not-paid'):
            conditions['is_paid'] = opt == 'paid'
        elif opt in ('at-swat', 'on-campus', 'off-campus'):
            conditions['at_swat'] = opt == 'off-campus'
        elif opt in ('filled', 'not-filled'):
            conditions['is_filled'] = opt == 'filled'
        elif opt in ('needs-car', 'no-car'):
            conditions['needs_car'] = opt == 'needs-car'
    
    jobs = JobListing.published.filter(**conditions).order_by('is_filled', '-pub_date')
    if 'limit' in request.GET:
        lim = request.GET['limit']
        if lim.isdigit():
            jobs = jobs[:int(lim)]
    else:
        jobs = jobs[:default_limit]
    
    data = {
        'jobs': jobs,
        'other_jobs': JobListing.unfilled.order_by('-pub_date')[:3]
    }
    
    rc = RequestContext(request)
    return render_to_response(template, data, context_instance=rc)


def submit_job(request, template="listings/jobs/submit.html"):
    if request.method == 'POST':
        form = SubmitJobForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse(job_success))
    else:
        form = SubmitJobForm()
    
    data = { 'form': form }
    rc = RequestContext(request)
    return render_to_response(template, data, context_instance=rc)

def job_success(request, template="listings/jobs/success.html"):
    return render_to_response(template, {}, context_instance=RequestContext(request))
