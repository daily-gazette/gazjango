from django.db.models           import Q
from django.http                import Http404
from django.template            import RequestContext
from django.shortcuts           import render_to_response
from gazjango.misc.view_helpers import get_by_date_or_404, filter_by_date
from gazjango.misc.view_helpers import staff_required, boolean_arg

from gazjango.athletics.models     import Team, Game
from gazjango.announcements.models import Announcement
from gazjango.articles.models      import Article
from gazjango.issues.models        import Issue, Menu, Event
from gazjango.jobs.models          import JobListing
from gazjango.comments.models      import PublicComment

import datetime

def issue_for_date(request, year, month, day, plain=False):
    issue = get_by_date_or_404(Issue, year, month, day, field='date')
    return show_issue(request, issue, plain)

def latest_issue(request, plain=False):
    return show_issue(request, Issue.with_articles.latest(), plain)

def show_issue(request, issue, plain=False):
    tomorrow = issue.date + datetime.timedelta(days=1)
    comments = PublicComment.visible.filter(time__lt=tomorrow).order_by('-time')
    
    one_week = datetime.timedelta(days=7)
    if issue.date == datetime.date.today():
        jobs = JobListing.unfilled.get_for_show(num=5, cutoff=one_week)
    else:
        jobs = JobListing.published.get_for_show(num=5, base_date=issue.date, cutoff=one_week)
    
    articles = issue.articles_in_order(racy=boolean_arg(request.GET.get('racy', ''), True))
    try:
        topstory = articles[0]
    except IndexError:
        raise Http404
    
    data = {
        'issue': issue,
        'topstory': articles[0],
        'midstories': articles[1:issue.num_full],
        'lowstories': articles[issue.num_full:],
        'jobs': jobs,
        'comments': comments[:5],
        'for_email': boolean_arg(request.GET.get('for_email', ''), False)
    }
    template = "issue/issue." + ('txt' if plain else 'html')
    return render_to_response(template, data)


@staff_required
def preview_issue(request, plain=False):
    issue, created = Issue.objects.populate_issue()
    try:
        resp = show_issue(request, issue, plain)
    finally:
        if created:
            issue.delete()
    return resp


def issues_list(request, year=None, month=None):
    issues = filter_by_date(Issue.objects.all(), year, month, field='date')
    data = {
        'issues': issues,
        'year': year,
        'month': month
    }
    rc = RequestContext(request)
    return render_to_response("issue/issues_list.html", data, context_instance=rc)



def datify(year, month, day):
    if not (year or month or day):
        return datetime.date.today()
    else:
        try:
            return datetime.date(int(year), int(month), int(day))
        except ValueError:
            raise Http404

def show_rsd(request, year=None, month=None, day=None, plain=False, date=None):
    return show_rsd_thing(request, date or datify(year, month, day), plain,
            regular=True, lost_and_found=True, jobs=True)

def show_events(request, year=None, month=None, day=None, plain=False, date=None):
    return show_rsd_thing(request, date or datify(year, month, day), plain,
            events=True)

def show_combined(request, year=None, month=None, day=None, plain=False, date=None):
    return show_rsd_thing(request, date or datify(year, month, day), plain,
            regular=True, events=True, lost_and_found=True, jobs=True)

def show_rsd_thing(request, date, plain=False,
                   regular=False, events=False, lost_and_found=False, jobs=False):
    """Show the RSD with some subset of sections."""
    
    if regular:
        regular = Announcement.regular.running_on(date).order_by('-date_start', 'pk')
    if events:
        events = Announcement.events.running_on(date).order_by('event_date', 'event_time', 'pk')
    if lost_and_found:
        lost_and_found = Announcement.lost_and_found.running_on(date).order_by('-date_start', 'pk')
    if jobs:
        midnight = datetime.datetime.combine(date, datetime.time(23, 59))
        jobs = JobListing.published.order_by('is_filled', '-pub_date') \
                     .filter(pub_date__lte=midnight) \
                     .filter(pub_date__gte=midnight - datetime.timedelta(days=7))
        if date == datetime.date.today():
            jobs = jobs.filter(is_filled=False)
    
    if not any(x.count() if x else 0 for x in (regular, events, lost_and_found, jobs)):
        raise Http404
    
    tomorrow = date + datetime.timedelta(days=1)
    comments = PublicComment.visible.filter(time__lt=tomorrow).order_by('-time')
    
    order = lambda x, *ord: x.order_by(*ord) if x else []
    data = {
        'year': date.year, 'month': date.month, 'day': date.day, 'date': date,
        'announcements': regular or [],
        'events': events or [],
        'jobs': jobs or [],
        'lost_and_found': lost_and_found or [],
        'comments': comments[:3],
        'stories': Article.published.order_by('-pub_date').filter(is_racy=False)[:3],
        'for_email': boolean_arg(request.GET.get('for_email', ''), False),
    }
    template = "issue/rsd." + ('txt' if plain else 'html')
    return render_to_response(template, data)

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
