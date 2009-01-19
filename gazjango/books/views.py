from django.contrib.auth.decorators import login_required
from django.core.urlresolvers       import reverse
from django.http      import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template  import RequestContext

from gazjango.articles.models   import Article
from gazjango.books.models      import BookListing
from gazjango.books.forms       import SubmitBookForm
from gazjango.comments.models   import PublicComment
from gazjango.misc.view_helpers import get_user_profile

def book_details(request, slug):
    book = get_object_or_404(BookListing, slug=slug)
    tops, mids, lows = Article.published.get_stories(num_top=1, num_mid=3, num_low=0)
    
    return render_to_response('books/details.html', {
        'book': book,
        'topstory': tops[0],
        'stories': mids,
        'comments': PublicComment.visible.order_by('-time')[:3],
        'other_books': BookListing.unfilled.order_by('-pub_date')[:3]
    }, context_instance=RequestContext(request))


def list_books(request):
    books = BookListing.published.filter(sold_at=None).order_by('-pub_date')
    tops, mids, lows = Article.published.get_stories(num_top=1, num_mid=3, num_low=0)
    
    return render_to_response('books/list.html', {
        'books': books,
        'topstory': tops[0],
        'stories': mids,
        'comments': PublicComment.visible.order_by('-time')[:3],
        'other_books': BookListing.unsold.order_by('-pub_date')[:3]
    }, context_instance=RequestContext(request))


@login_required
def submit_book(request):
    needs_email = not request.user.email
    if request.method == 'POST':
        form = SubmitBookForm(request.POST, needs_email=needs_email)
        if form.is_valid():
            book = form.save(commit=False)
            profile = get_user_profile(request)
            book.seller = profile
            book.save()
            if needs_email:
                profile.user.email = form.cleaned_data['email']
                profile.save()
            form.save_m2m()
            return HttpResponseRedirect(reverse(book_success))
    else:
        form = SubmitBookForm(needs_email=needs_email)
    
    return render_to_response('books/submit.html', {
        'form': form,
    }, context_instance=RequestContext(request))


def book_success(request, template="books/success.html"):
    return render_to_response(template, {}, context_instance=RequestContext(request))
