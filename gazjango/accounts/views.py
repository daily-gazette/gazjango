from django.template import RequestContext
from django.contrib.auth.decorators import permission_required
from django.shortcuts import render_to_response

from announcements.models import Announcement
from articles.models      import StoryConcept, ArticleRevision
from comments.models      import PublicComment

manage       = lambda request, **kwargs: render_to_response("base.html", locals())
register     = lambda request, **kwargs: render_to_response("base.html", locals())
user_details = lambda request, **kwargs: render_to_response("base.html", locals())

@permission_required('accounts.can_access_admin')
def admin_index(request, template="custom-admin/index.html"):
    user = request.user.get_profile()
    articles = user.articles.all().order_by('-pub_date')
    
    announcements = Announcement.admin.order_by('-date_start')
    
    data = {
        'articles': articles,
        'announcement': announcements[0] if announcements.count() > 0 else None,
        'unclaimed': StoryConcept.unpublished.filter(users=None),
        'others': StoryConcept.unpublished.exclude(users=user),
    
        'revisions': ArticleRevision.objects.filter(article__in=articles).order_by('-date'),
        'comments': PublicComment.objects.filter(article__in=articles).order_by('-time')
    }
    
    rc = RequestContext(request)
    return render_to_response(template, context_instance=rc)
