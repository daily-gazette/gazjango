from django.http             import HttpResponseRedirect, Http404
from django.shortcuts        import get_object_or_404, render_to_response
from django.template         import loader, RequestContext
from django.utils.safestring import mark_safe
from gazjango.misc.view_helpers   import get_user_profile
from gazjango.stackedpages.models import Page
from gazjango.articles.models     import Article
from gazjango.comments.models     import PublicComment
from gazjango.announcements.models import Poster

from django.conf import settings

DEFAULT_TEMPLATE = 'flatpages/default.html'

def page(request, url):
    'View for "stacked" pages.'
    
    if not url.endswith('/') and settings.APPEND_SLASH:
        url += '/'
    if not url.startswith('/'):
        url = '/' + url
    
    page = get_object_or_404(Page, url__exact=url, sites__id__exact=settings.SITE_ID)
    
    if page.staff_only:
        user = get_user_profile(request)
        if not user.is_staff:
            raise Http404
    
    page.title = mark_safe(page.title)
    page.content = mark_safe(page.formatted_content())
    
    if page.template_name:
        template = (f.template_name, DEFAULT_TEMPLATE)
    else:
        template = DEFAULT_TEMPLATE
    
    tops, mids, lows = Article.published.get_stories(num_top=1, num_mid=3, num_low=0)
    rc = RequestContext(request)
    context = {
        'page': page,
        'topstory': tops[0],
        'stories': mids,
        'comments': PublicComment.visible.order_by('-time')[:3],
        'poster': Poster.published.get_running(),
    }
    
    return render_to_response(template, context, context_instance=rc)
