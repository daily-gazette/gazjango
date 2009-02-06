from django.contrib import admin
from gazjango.screw.models import ScrewListing

class ScrewAdmin(admin.ModelAdmin):
    list_display = ('screwee', 'screwer', 'year', 'screwed_at')
    list_filter = ('is_published',)
    date_hierarchy = 'pub_date'
    
    fieldsets = (
        (None, {
            'fields': ('screwee', 'screwer', 'year'),
        })
    )
    prepopulated_fields = { 'slug': ('screwee',) }
admin.site.register(ScrewListing, ScrewAdmin)
