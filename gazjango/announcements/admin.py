from django.contrib import admin
from gazjango.announcements.models import Announcement, Poster
import datetime

class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('slug', 'title', 'unlinked_excerpt', 'is_published', 
                    'is_event', 'is_lost_and_found', 'date_start', 'date_end')
    list_filter = ('is_published', 'kind', 'is_lost_and_found')
    search_fields = ('slug', 'title', 'text', 'sponsor')
    date_hierarchy = 'date_start'
    save_as = True

    actions = ['make_published', 'start_today']

    def make_published(self, request, queryset):
        rows_updated = queryset.update(is_published=True)
        if rows_updated == 1:
            message_bit = "1 announcement was"
        else:
            message_bit = "%s announcements were" % rows_updated
        self.message_user(request, "%s successfully marked as published." % message_bit)
    make_published.short_description = "Mark announcements as published"
    
    def start_today(self, request, queryset):
        rows_updated = queryset.update(date_start=datetime.date.today())
        if rows_updated == 1:
            message_bit = "1 announcement was"
        else:
            message_bit = "%s announcements were" % rows_updated
        self.message_user(request, "%s successfully set to start today." % message_bit)
    start_today.short_description = "Set announcements' start date to today"


admin.site.register(Announcement, AnnouncementAdmin)

class PosterAdmin(admin.ModelAdmin):
    list_display = ('title', 'sponsor_user', 'is_published', 'date_start', 'date_end')
    list_filter = ('is_published',)
    save_as = True
admin.site.register(Poster, PosterAdmin)
