from django.http                   import HttpResponseRedirect
from django.template               import RequestContext
from django.core.urlresolvers      import reverse
from django.shortcuts              import render_to_response, get_object_or_404

from gazjango.misc.view_helpers    import get_by_date_or_404, filter_by_date
from gazjango.announcements.models import Announcement
from gazjango.announcements.forms  import SubmitAnnouncementForm
from gazjango.articles.models      import Article
from gazjango.issues.models        import Issue, Menu, Event
from gazjango.jobs.models          import JobListing
from gazjango.jobs.forms           import SubmitJobForm
from gazjango.comments.models      import PublicComment
from gazjango.reviews.directions   import TRAIN_STATIONS
from gazjango.reviews.models       import Establishment, Review
from gazjango.reviews.forms        import SubmitEstablishmentForm, SubmitReviewForm
from gazjango.housing.models       import HousingListing
from gazjango.housing.forms        import SubmitHousingForm
from gazjango.misc.view_helpers    import get_user_profile

import datetime

def announcement(request, slug, year, month=None, day=None):
    an = get_object_or_404(Announcement, slug=slug, date_start__year=year)
    data = {
        'announcement': an,
        'recent_announcements': Announcement.community.order_by('-date_end')[:4],
    }
    rc = RequestContext(request)
    return render_to_response("listings/announcements/details.html", data, context_instance=rc)


def list_announcements(request, kind=None, year=None, month=None, day=None, order='d'):
    if (request.GET.get('order', None) or order).startswith('d'):
        qset = Announcement.community.order_by('-date_end', '-date_start')
    else:
        qset = Announcement.community.order_by('date_end', 'date_start')
    
    if year:
        qset = filter_by_date(qset, year, month, day, field='date_start')
    else:
        qset = qset.exclude(date_start__gt=datetime.date.today())
    
    if kind:
        qset = qset.filter(kind=kind)
    
    events = qset.exclude(event_date=None)
    non_events = qset.filter(event_date=None)
    
    data = { 
        'announcements': qset,
        'kind': kind,
        'year': year,
        'month': month,
        'day': day,
        'events': events.order_by('event_date', 'event_time', 'pk'),
        'non_events': non_events,
        'recent_announcements': Announcement.community.order_by('-date_end')[:4],
    }
    rc = RequestContext(request)
    return render_to_response("listings/announcements/list.html", data, context_instance=rc)

def submit_announcement(request, template="listings/announcements/submit.html"):
    if request.method == 'POST':
        form = SubmitAnnouncementForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse(announcement_success))
    else:
        form = SubmitAnnouncementForm()
    
    data = { 'form': form }
    rc = RequestContext(request)
    return render_to_response(template, data, context_instance=rc)


def announcement_success(request, template="listings/announcements/success.html"):
    return render_to_response(template, {}, context_instance=RequestContext(request))
    
 
def around_swarthmore(request,template = "listings/around/index.html"):
    today = datetime.date.today()
    year = today.year
    month = today.month
    day = today.day
    
    date = datetime.date(int(year), int(month), int(day))
    current = Announcement.community.filter(date_start__lte=date, date_end__gte=date)

    regular = current.filter(is_lost_and_found=False, event_date=None)
    events = current.exclude(event_date=None)
    lost_and_found = current.filter(is_lost_and_found=True)

    one_week = datetime.timedelta(days=7)
    if date == datetime.date.today():
        jobs = JobListing.unfilled.get_for_show(num=5, cutoff=one_week)
    else:
        jobs = JobListing.published.get_for_show(num=5, base_date=date, cutoff=one_week)

    if not current.count() and not jobs.count():
        raise Http404

    tomorrow = date + datetime.timedelta(days=1)
    comments = PublicComment.visible.filter(time__lt=tomorrow).order_by('-time')

    t,m,l = Article.published.get_stories(num_top=0, num_mid=4, num_low=0, base=base)
    try:
        topstory = articles[0]
    except IndexError:
        raise Http404
        

    if request.method == 'POST':
        announcement_form = SubmitAnnouncementForm()
        job_form = SubmitJobForm()
        
        if announcement_form.is_valid():
            announcement_form.save_m2m()
            return HttpResponseRedirect(reverse(around_swarthmore))
            
        if job_form.is_valid():
            job_form.save_m2m()
            return HttpResponseRedirect(reverse(around_swarthmore))
    else:
        announcement_form = SubmitAnnouncementForm()
        job_form = SubmitJobForm()

    data = {
        'year': year, 'month': month, 'day': day,
        'date': date,
        'announcements': regular.order_by('-date_start', 'pk'),
        'events': events.order_by('event_date', 'event_time', 'pk'),
        'lost_and_found': lost_and_found.order_by('-date_start', 'pk'),
        'jobs': jobs,
        'comments': comments[:10],
        'stories': m,
        'announcement_form': announcement_form,
        'job_form': job_form,
    }
    rc = RequestContext(request)
    return render_to_response(template, data,context_instance=rc)
