from django.db.models               import Q
from django.contrib.auth.decorators import permission_required
from django.http                    import HttpResponse, Http404, HttpResponseRedirect
from django.template                import RequestContext
from django.shortcuts               import render_to_response
from gazjango.misc.view_helpers     import get_by_date_or_404, reporter_admin_data
from gazjango.misc.view_helpers     import get_ip, get_user_profile, is_robot

from gazjango.articles.models      import Article, StoryConcept
from gazjango.announcements.models import Announcement
from gazjango.comments.models      import PublicComment

def comments_for_article(request, slug, year, month, day, num=None):
    """
    Returns the comments for the specified article, rendered as they are
    on article view pages, starting after number `num`. Used for after
    you've posted an AJAX comment.
    """
    story = get_by_date_or_404(Article, year, month, day, slug=slug)
    
    user = get_user_profile(request)
    ip = get_ip(request)
    
    spec = Q(number__gt=num) if num else Q()
    comments = PublicComment.objects.for_article(story, user, ip, spec=spec)
    
    rc = RequestContext(request, { 'comments': comments, 'new': True })
    return render_to_response("stories/comments.html", context_instance=rc)


def get_comment_text(request, slug, year, month, day, num):
    story = get_by_date_or_404(Article, year, month, day, slug=slug)
    try:
        comment = story.comments.get(number=num)
    except PublicComment.DoesNotExist:
        raise Http404
    return HttpResponse(comment.text)


def vote_on_comment(request, slug, year, month, day, num, val):
    story = get_by_date_or_404(Article, year, month, day, slug=slug)
    try:
        comment = story.comments.get(number=num)
    except PublicComment.DoesNotExist:
        raise Http404
    
    if is_robot(request):
        return HttpResponse('sorry, you seem to be a robot, no voting for you!')
    
    positive = (val == 'up') if val in ('up', 'down') else None
    result = comment.vote(positive, ip=get_ip(request), user=get_user_profile(request))
    
    if request.is_ajax():
        return HttpResponse("success" if result else "failure")
    else:
        return HttpResponseRedirect(comment.get_absolute_url())


@permission_required('accounts.can_access_admin')
def manage(request, template="custom-admin/comments.html"):
    data = reporter_admin_data(get_user_profile(request))
    data['comments'] = PublicComment.objects.order_by('-time')
    
    rc = RequestContext(request)
    return render_to_response(template, data, context_instance=rc)
