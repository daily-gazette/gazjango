from django.contrib import admin
from gazjango.ads.models import TextLinkAd

class TextLinkAdAdmin(admin.ModelAdmin):
    list_display = ('text', 'link', 'source')
    list_filter = ('source',)
admin.site.register(TextLinkAd, TextLinkAdAdmin)
