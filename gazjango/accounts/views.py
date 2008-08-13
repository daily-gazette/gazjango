from django.http import HttpResponse, Http404
from django.template import RequestContext
from django.contrib.auth.decorators import permission_required
from django.shortcuts import render_to_response
from django.db.models import Q

from django.contrib.auth.models import User
from accounts.models      import UserProfile
from announcements.models import Announcement
from articles.models      import StoryConcept, ArticleRevision
from comments.models      import PublicComment

manage       = lambda request, **kwargs: render_to_response("base.html", locals())
register     = lambda request, **kwargs: render_to_response("registration/register.html", locals())
user_details = lambda request, **kwargs: render_to_response("base.html", locals())

@permission_required('accounts.can_access_admin')
def admin_index(request, template="custom-admin/index.html"):
    user = request.user.get_profile()
    articles = user.articles.all().order_by('-pub_date')
    announcements = Announcement.admin.order_by('-date_start')
    
    data = {
        'announcement': announcements[0] if announcements.count() else None,
        'unclaimed': StoryConcept.unpublished.filter(users=None),
        'others': StoryConcept.unpublished.exclude(users=user),
        
        'articles': articles,
        'revisions': ArticleRevision.objects.filter(article__in=articles).order_by('-date'),
        'comments': PublicComment.visible.filter(article__in=articles).order_by('-time')
    }
    
    rc = RequestContext(request)
    return render_to_response(template, context_instance=rc)


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
        if request.method == 'POST':
            name = request.POST['name']
        else:
            name = request.GET['name']
    except KeyError:
        raise Http404
    
    split = name.split()
    length = len(split)
    if length < 2:
        raise Http404
    elif length == 2:
        first, last = split
    else:
        for i in range(1, len(split)):
            first = ' '.join(split[:i])
            last  = ' '.join(split[i:])
            matches = User.objects.filter(
                first_name__iexact=first,
                last_name__iexact=last
            )
            if matches.count():
                break
    
    try:
        u = User.objects.get(first_name__iexact=first, last_name__iexact=last)
        return HttpResponse(u.username)
    except User.DoesNotExist:
        # if request.method == 'POST' and request.user.has_perm('auth.add_user'):
        if request.user.has_perm('auth.add_user'):
            u = UserProfile.objects.create_lite_user(first, last).user
            return HttpResponse(u.username)
        else:
            raise Http404
