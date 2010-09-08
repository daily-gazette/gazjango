from django.contrib.auth  import views as auth_views
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models     import User
from django.db.models     import Q
from django.http          import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts     import render_to_response, get_object_or_404
from django.template      import RequestContext

import datetime

from gazjango.accounts.models      import UserProfile
from gazjango.misc.view_helpers    import get_user_profile
from gazjango.subscriptions.models import Subscriber

@login_required
def manage(request, template="accounts/manage.html"):
    profile = get_user_profile(request)
    subscribers = Subscriber.issues.filter(user=profile)

    rc = RequestContext(request, {
            'subscriber': subscribers[0] if subscribers else None,
        })
    return render_to_response(template, context_instance=rc)

@login_required
def racy_switch(request, val):
    profile = get_user_profile(request)
    Subscriber.issues.filter(user=profile).update(racy_content=(val == "on"))
    return HttpResponseRedirect('/accounts/manage/')

@login_required
def unsubscribe(request):
    profile = get_user_profile(request)
    today = datetime.datetime.today()
    Subscriber.issues.filter(user=profile).update(unsubscribed=today)
    return HttpResponseRedirect('/accounts/manage/')

@login_required
def subscribe(request):
    profile = get_user_profile(request)
    if profile.kind:
        racy = profile.kind.kind in 'sk'
    else:
        racy = False
    Subscriber.objects.create(receive='i', user=profile, racy_content=racy)
    return HttpResponseRedirect('/accounts/manage/')


def logout(request, next_page='/'):
    from gazjango.facebook_connect.middleware import FacebookConnectMiddleware
    FacebookConnectMiddleware.delete_fb_cookies = True
    return auth_views.logout(request, next_page=next_page)


def user_details(request, name, template="accounts/profile.html"):
    """Shows a user's profile page."""
    relevant = UserProfile.objects.exclude(Q(positions=None) & Q(articles=None))
    return render_to_response(template, {
        'author': get_object_or_404(relevant.distinct(), user__username=name)
    }, context_instance=RequestContext(request))


def author_completions(request):
    if 'q' in request.GET:
        q = request.GET['q']
        parts = q.split()
        queries = [ Q(user__username__icontains=part) | \
                    Q(user__first_name__icontains=part) | \
                    Q(user__last_name__icontains=part) \
                    for part in parts ]
        query = reduce(lambda q1, q2: q1 & q2, queries)
    else:
        query = Q()
    
    matches = UserProfile.objects.filter(query)
    lst = ["%s|%s" % (match.name, match.username) for match in matches]
    return HttpResponse("\n".join(lst))


def username_for_name(request):
    """
    Returns the username for the user in request.POST['name']. If there
    is no such user, calls ``create_lite_user`` to make one.
    
    If this is called with GET, will return the username if one is found,
    but will 404 rather than creating a user on failure, as GETs should
    not have side effects.
    
    If there's more than one space, tries to figure it out, but
    it might be flakey.
    """
    try:
        name = (request.POST if request.method == 'POST' else request.GET)['name']
    except KeyError:
        raise Http404
    
    try:
        create = request.method == 'POST' and request.user.has_perm('auth.add_user')
        username = UserProfile.objects.username_for_name(name, create=create)
    except User.DoesNotExist:
        raise Http404
