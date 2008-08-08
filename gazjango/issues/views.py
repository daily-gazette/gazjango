from django.template   import RequestContext
from django.shortcuts  import render_to_response
from misc.view_helpers import get_by_date_or_404, filter_by_date

from issues.models   import Issue, Menu
from jobs.models     import JobListing
from comments.models import PublicComment

import datetime

def issue(request, year, month, day):
    issue = get_by_date_or_404(Issue, year, month, day, field='date')
    data = {
        'issue': issue,
        'jobs': JobListing.objects.order_by('-pub_date').filter(is_filled=False)[:5],
        'comments': PublicComment.visible.order_by('-time')[:5]
    }
    rc = RequestContext(request)
    from django.http import HttpResponse
    return render_to_response("issue/issue.html", data, context_instance=rc)


def issue_for_today(request):
    today = datetime.date.today()
    return issue(request, today.year, today.month, today.day)


def issues_list(request, year=None, month=None):
    issues = filter_by_date(Issue.objects.all(), year, month, field='date')
    data = {
        'issues': issues,
        'year': year,
        'month': month
    }
    rc = RequestContext(request)
    return render_to_response("issue/issues_list.html", data, context_instance=rc)


def menu_partial(request):
    if datetime.datetime.now().hour < 21:
        menu = Menu.objects.for_today()
    else:
        menu = Menu.objects.for_tomorrow()
    return render_to_response("scraped/menu.html", { 'menu': menu })

