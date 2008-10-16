from django.contrib.auth.decorators import permission_required
from django.http                import HttpResponse, Http404, HttpResponseRedirect
from django.template            import RequestContext
from django.shortcuts           import render_to_response
from gazjango.misc.view_helpers import get_by_date_or_404, reporter_admin_data

from gazjango.articles.models      import Article, StoryConcept
from gazjango.announcements.models import Announcement
from gazjango.comments.models      import PublicComment


def get_comment_text(request, slug, year, month, day, num):
    story = get_by_date_or_404(Article, year, month, day, slug=slug)
    try:
        comment = story.comments.get(number=num)
    except PublicComment.DoesNotExist:
        raise Http404
    return HttpResponse(comment.text)


def vote_on_comment(request, slug, year, month, day, num, val):
    story = get_by_date_or_404(Article, year, month, day, slug=slug)
    positive = True if val == 'up' else (False if val == 'down' else None)
    try:
        comment = story.comments.get(number=num)
    except PublicComment.DoesNotExist:
        raise Http404
    
    user = request.user.get_profile() if request.user.is_authenticated() else None
    ip = request.META['REMOTE_ADDR']
    result = comment.vote(positive, ip=ip, user=user)
    
    if request.is_ajax():
        return HttpResponse("success" if result else "failure")
    else:
        return HttpResponseRedirect(comment.get_absolute_url())


@permission_required('accounts.can_access_admin')
def manage(request, template="custom-admin/comments.html"):
    data = reporter_admin_data(request.user.get_profile())
    data['comments'] = PublicComment.objects.order_by('-time')
    
    rc = RequestContext(request)
    return render_to_response(template, data, context_instance=rc)
