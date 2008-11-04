from django.contrib import admin
from gazjango.announcements.models import Announcement

class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('slug', 'name', 'brief_excerpt', 'is_published', 'is_event', 'date_start', 'date_end')
    list_filter = ('is_published', 'kind')
admin.site.register(Announcement, AnnouncementAdmin)
