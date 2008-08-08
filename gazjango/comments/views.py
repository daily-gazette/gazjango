from django.http import HttpResponse, Http404
from misc.view_helpers import get_by_date_or_404

from articles.models import Article
from models          import PublicComment


def get_comment_text(request, slug, year, month, day, num):
    story = get_by_date_or_404(Article, year, month, day, slug=slug)
    try:
        comment = story.comments.get(number=num)
        return HttpResponse(comment.text)
    except PublicComment.DoesNotExist:
        raise Http404
