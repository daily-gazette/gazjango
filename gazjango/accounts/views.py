from django.http import HttpResponse, Http404
from django.template import RequestContext
from django.contrib.auth.decorators import permission_required
from django.shortcuts import render_to_response, get_object_or_404
from django.db.models import Q
from gazjango.misc.view_helpers import get_user_profile

from django.contrib.auth.models import User
from gazjango.accounts.models import UserProfile
from gazjango.articles.models import ArticleRevision
from gazjango.comments.models import PublicComment

def manage(requset):
    raise Http404 # temporary, obviously


def user_details(request, name, template="accounts/profile.html"):
    """Shows a user's profile page."""
    up = get_object_or_404(UserProfile, user__username=name, user__is_staff=True)
    rc = RequestContext(request)
    return render_to_response(template, {'author': up}, context_instance=rc)


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
