from django.contrib import admin
from gazjango.ads.models import TextLinkAd, BannerAd
# from gazjango.media.models import ImageFile

class TextLinkAdAdmin(admin.ModelAdmin):
    list_display = ('text', 'link', 'source')
    list_filter = ('source',)
admin.site.register(TextLinkAd, TextLinkAdAdmin)

class BannerAdAdmin(admin.ModelAdmin):
    list_display = ('publisher', 'space', 'date_start', 'date_end')
    list_filter = ('space', 'publisher')
    search_fields = ('slug', 'publisher', 'description')
    date_hierarchy = 'date_start'
    
    fieldsets = (
            (None, {
                'fields': ('publisher', 'space', 'link', 'priority'),
            }),
            ('Content', {
                'fields': ('render_type', 'image', 'outside'),
            }),
            ('Timing', {
                'fields': ('date_start', 'date_end'),
            }),
            ('Other', {
                'fields': ('description',),
                'classes': ('collapse',),
            })
        )
admin.site.register(BannerAd, BannerAdAdmin)