from django.core.urlresolvers import reverse
from django.http              import HttpResponseRedirect
from django.template          import RequestContext
from django.shortcuts         import render_to_response, get_object_or_404
from gazjango.books.models     import BookListing
from gazjango.books.forms      import SubmitBookForm
from gazjango.articles.models import Article
from gazjango.comments.models import PublicComment

def book_details(request, slug, template="books/details.html"):
    book = get_object_or_404(BookListing, slug=slug)
    tops, mids, lows = Article.published.get_stories(num_top=1, num_mid=3, num_low=0)
    data = {
        'book': ,
        'topstory': tops[0],
        'stories': mids,
        'comments': PublicComment.visible.order_by('-time')[:3],
        'other_books': BookListing.unfilled.order_by('-pub_date')[:3]
    }
    rc = RequestContext(request)
    return render_to_response(template, data, context_instance=rc)


def list_books(request, options="", default_limit=10, template="books/list.html"):

    books = BookListing.published.filter(**conditions).order_by('is_sold', '-pub_date')
    if 'limit' in request.GET:
        lim = request.GET['limit']
        if lim.isdigit():
            books = books[:int(lim)]
    else:
        books = books[:default_limit]
    
    tops, mids, lows = Article.published.get_stories(num_top=1, num_mid=3, num_low=0)
    data = {
        'books': books,
        'topstory': tops[0],
        'stories': mids,
        'comments': PublicComment.visible.order_by('-time')[:3],
        'other_books': BookListing.unfilled.order_by('-pub_date')[:3]
    }
    
    rc = RequestContext(request)
    return render_to_response(template, data, context_instance=rc)


def submit_book(request, template="books/submit.html"):
    if request.method == 'POST':
        form = SubmitBookForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse(book_success))
    else:
        form = SubmitBookForm()
    
    data = { 'form': form }
    rc = RequestContext(request)
    return render_to_response(template, data, context_instance=rc)

def book_success(request, template="books/success.html"):
    return render_to_response(template, {}, context_instance=RequestContext(request))
