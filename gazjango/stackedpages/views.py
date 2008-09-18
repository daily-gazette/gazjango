from django.http             import HttpResponseRedirect
from django.shortcuts        import get_object_or_404, render_to_response
from django.template         import loader, RequestContext
from django.utils.safestring import mark_safe
from gazjango.stackedpages.models import Page
from gazjango.articles.models     import Article
from gazjango.comments.models     import PublicComment
from django.conf import settings

DEFAULT_TEMPLATE = 'flatpages/default.html'

def page(request, url):
    'View for "stacked" pages.'
    
    if not url.endswith('/') and settings.APPEND_SLASH:
        url += '/'
    if not url.startswith('/'):
        url = '/' + url
    
    page = get_object_or_404(Page, url__exact=url, sites__id__exact=settings.SITE_ID)
    
    page.title = mark_safe(page.title)
    page.content = mark_safe(page.content)
    
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
        'comments': PublicComment.visible.order_by('-time')[:3]
    }
    
    return render_to_response(template, context, context_instance=rc)
