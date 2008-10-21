from django.contrib import admin
from gazjango.announcements.models import Announcement

class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'is_published', 'is_event', 'date_start', 'date_end', 'kind')
    list_filter = ('is_published', 'is_event', 'kind')
admin.site.register(Announcement, AnnouncementAdmin)
