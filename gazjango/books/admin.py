from django.contrib import admin
from gazjango.books.models import BookListing

class BookAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_published', 'pub_date', 'book_seller', 'is_filled')
    list_filter = ('is_published', 'is_sold')
    date_hierarchy = 'pub_date'
admin.site.register(BookListing, BookAdmin)
