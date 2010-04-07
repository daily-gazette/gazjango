from gazjango.comments.models import PublicComment
from gazjango.misc.helpers import cache
import heapq

NUM_CONSIDERED = 50
NUM_RETURNED = 6

@cache(60 * 60)
def popular_comments(request, range=NUM_CONSIDERED, num=NUM_RETURNED):
    return {
        'popular_comments': heapq.nlargest(num,
            PublicComment.objects.order_by('-time')[:range],
            key=lambda c: c.score),
    }
