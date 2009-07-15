from gazjango.community.models import *
from gazjango.community.sources.flickr import *
from django.contrib import admin

class EntryAdmin(admin.ModelAdmin):
    list_display = ('title', 'url',)
    list_filter = ('source_type',)
    radio_fields = {'status': admin.VERTICAL}
    date_hierarchy = 'timestamp'
    fieldsets = (
        (None, {
            'fields':('title','description','status'),
        }),
        ('Advanced', {
            'fields': ('timestamp','owner_user','url','source_type'),
            'classes': ('collapse',),
        })
    )

# admin definition
class FlickrPhotoAdmin(admin.ModelAdmin):
    list_display = ('photo_id', 'title', 'taken_at', 'uploaded_at',)
    date_hierarchy = 'uploaded_at'

admin.site.register(FlickrPhoto, FlickrPhotoAdmin)
admin.site.register(Entry, EntryAdmin)