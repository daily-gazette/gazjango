from django.core.urlresolvers import reverse
from django.http              import HttpResponseRedirect
from django.template          import RequestContext
from django.shortcuts         import render_to_response, get_object_or_404
from jobs.models     import JobListing
from jobs.forms      import SubmitJobForm
from articles.models import Article
from comments.models import PublicComment

def job_details(request, slug, template="jobs/details.html"):
    job = get_object_or_404(JobListing, slug=slug)
    tops, mids, lows = Article.published.get_stories(num_top=1, num_mid=3, num_low=0)
    data = {
        'job': job,
        'topstory': tops[0],
        'stories': mids,
        'comments': PublicComment.visible.order_by('-time')[:3],
        'other_jobs': JobListing.unfilled.order_by('-pub_date')[:3]
    }
    rc = RequestContext(request)
    return render_to_response(template, data, context_instance=rc)


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
    
    tops, mids, lows = Article.published.get_stories(num_top=1, num_mid=3, num_low=0)
    data = {
        'jobs': jobs,
        'topstory': tops[0],
        'stories': mids,
        'comments': PublicComment.visible.order_by('-time')[:3],
        'other_jobs': JobListing.unfilled.order_by('-pub_date')[:3]
    }
    
    rc = RequestContext(request)
    return render_to_response(template, data, context_instance=rc)


def submit_job(request, template="jobs/submit.html"):
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

def job_success(request, template="jobs/success.html"):
    return render_to_response(template, {}, context_instance=RequestContext(request))
