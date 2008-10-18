from django.db.models           import Q
from django.template            import RequestContext
from django.shortcuts           import render_to_response
from gazjango.misc.view_helpers import get_by_date_or_404, filter_by_date

from gazjango.announcements.models import Announcement
from gazjango.issues.models        import Issue, Menu, Event
from gazjango.jobs.models          import JobListing
from gazjango.comments.models      import PublicComment

import datetime

def issue_for_date(request, year, month, day):
    issue = get_by_date_or_404(Issue, year, month, day, field='date')
    return show_issue(request, issue)

def latest_issue(request):
    return show_issue(request, Issue.objects.latest())

def show_issue(request, issue):
    data = {
        'issue': issue,
        'jobs': JobListing.unfilled.order_by('-pub_date')[:5],
        'comments': PublicComment.visible.order_by('-time')[:5]
    }
    rc = RequestContext(request, data)
    return render_to_response("issue/issue.html", context_instance=rc)


def issues_list(request, year=None, month=None):
    issues = filter_by_date(Issue.objects.all(), year, month, field='date')
    data = {
        'issues': issues,
        'year': year,
        'month': month
    }
    rc = RequestContext(request)
    return render_to_response("issue/issues_list.html", data, context_instance=rc)


def rsd_now(request, template="issue/rsd.html"):
    today = datetime.date.today()
    return show_rsd(request, today.year, today.month, today.day, template)

def show_rsd(request, year, month, day, template="issue/rsd.html"):
    date = datetime.date(int(year), int(month), int(day))
    not_event = Q(event_date=None)
    current = Announcement.community.filter(date_start__lte=date, date_end__gte=date)
    
    one_week = datetime.timedelta(days=7)
    if date == datetime.date.today():
        jobs = JobListing.unfilled.get_for_show(cutoff=one_week)
    else:
        jobs = JobListing.published.get_for_show(base_date=date, cutoff=one_week)
    
    tomorrow = date + datetime.timedelta(days=1)
    comments = PublicComment.visible.filter(time__lte=tomorrow).order_by('-time')
    stories = []
    data = {
        'year': year, 'month': month, 'day': day,
        'announcements': current.filter(not_event),
        'events': current.exclude(not_event),
        'jobs': jobs,
        'comments': comments[:5],
        'stories': stories
    }
    rc = RequestContext(request, data)
    return render_to_response(template, context_instance=rc)



def menu_partial(request):
    if datetime.datetime.now().hour < 21:
        menu = Menu.objects.for_today()
    else:
        menu = Menu.objects.for_tomorrow()
    return render_to_response("scraped/menu.html", { 'menu': menu })


def events_partial(request):
    today = datetime.date.today()
    events = Event.objects.for_date(today, forward=datetime.timedelta(days=40))
    return render_to_response("scraped/events.html", {'events': events})
