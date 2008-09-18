from django.contrib import admin
from gazjango.announcements.models import Announcement

class AnnouncementAdmin(admin.ModelAdmin):
    pass
admin.site.register(Announcement, AnnouncementAdmin)
