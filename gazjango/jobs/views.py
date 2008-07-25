from django.template  import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from jobs.models      import JobListing

def job_details(request, slug, template="jobs/details.html"):
    job = get_object_or_404(JobListing, slug=slug)
    rc = RequestContext(request)
    return render_to_response(template, {'job': job}, context_instance=rc)


def list_jobs(request, options="", default_limit=20, template="jobs/list.html"):
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
    
    jobs = JobListing.objects.filter(**conditions)
    
    if 'limit' in request.GET:
        lim = request.GET['limit']
        if lim.isdigit():
            jobs = jobs[:int(lim)]
    else:
        jobs = jobs[:default_limit]
    
    rc = RequestContext(request)
    return render_to_response(template, {'jobs': jobs}, context_instance=rc)
