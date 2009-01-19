from django.contrib import admin
from gazjango.books.models import BookListing

class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_published', 'pub_date', 'sold_at', 'seller')
    list_filter = ('is_published',)
    date_hierarchy = 'pub_date'
    
    fieldsets = (
        (None, {
            'fields': ('title', 'seller', 'departments', 'classes',
                       'cost', 'description', 'is_published'),
        }),
        ('Advanced', {
            'fields': ('slug', 'pub_date', 'sold_at'),
            'classes': ('collapse',),
        }),
    )
    prepopulated_fields = { 'slug': ('title',) }
    filter_horizontal = ('departments',)
admin.site.register(BookListing, BookAdmin)
