from gazjango.comments.models import PublicComment
import heapq

NUM_CONSIDERED = 50
NUM_RETURNED = 6

def popular_comments(request):
    return {
        'popular_comments': heapq.nlargest(NUM_RETURNED,
            PublicComment.objects.order_by('-time')[:NUM_CONSIDERED],
            key=PublicComment.num_upvotes)
    }
