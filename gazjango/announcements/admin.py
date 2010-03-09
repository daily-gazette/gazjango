from django.contrib import admin
from gazjango.announcements.models import Announcement, Poster

class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('slug', 'title', 'unlinked_excerpt', 'is_published', 
                    'is_event', 'is_lost_and_found', 'date_start', 'date_end')
    list_filter = ('is_published', 'kind', 'is_lost_and_found')
    search_fields = ('slug', 'title', 'text', 'sponsor')
    date_hierarchy = 'date_start'
admin.site.register(Announcement, AnnouncementAdmin)

class PosterAdmin(admin.ModelAdmin):
    list_display = ('title', 'sponsor_user', 'is_published', 'date_start', 'date_end')
    list_filter = ('is_published',)
admin.site.register(Poster, PosterAdmin)
