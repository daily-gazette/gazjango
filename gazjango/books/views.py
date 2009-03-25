from django.contrib.auth.decorators import login_required
from django.core.urlresolvers       import reverse
from django.http      import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template  import RequestContext

from gazjango.books.models      import BookListing
from gazjango.books.forms       import SubmitBookForm
from gazjango.misc.view_helpers import get_user_profile

import datetime

def book_details(request, slug):
    book = get_object_or_404(BookListing, slug=slug)
    
    return render_to_response('listings/books/details.html', {
        'book': book,
        'other_books': BookListing.unfilled.order_by('-pub_date')[:3]
    }, context_instance=RequestContext(request))


def list_books(request):
    books = BookListing.published.filter(sold_at=None).order_by('-pub_date')
    profile = get_user_profile(request)
    
    return render_to_response('listings/books/list.html', {
        'books': books,
        'user_profile': profile,
    }, context_instance=RequestContext(request))


def mark_as_sold(request, slug):
    book = get_object_or_404(BookListing, slug=slug)
    profile = get_user_profile(request)
    
    if profile and profile == book.seller:
        book.sold_at = datetime.datetime.now()
        book.save()
        if request.is_ajax():
            return HttpResponse('success')
        else:
            return HttpResponseRedirect(reverse(list_books))
    else:
        if request.is_ajax():
            return 'denied'
        else:
            raise Http404


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
                profile.user.save()
            form.save_m2m()
            # return HttpResponseRedirect(reverse(book_success))
            return HttpResponseRedirect(reverse(list_books))
    else:
        form = SubmitBookForm(needs_email=needs_email)
    
    return render_to_response('listings/books/submit.html', {
        'form': form,
    }, context_instance=RequestContext(request))


def book_success(request, template="books/success.html"):
    return render_to_response(template, {}, context_instance=RequestContext(request))
