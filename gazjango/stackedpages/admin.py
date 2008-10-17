from django.contrib import admin
from gazjango.stackedpages.models import Page

class PageAdmin(admin.ModelAdmin):
    pass
admin.site.register(Page, PageAdmin)
