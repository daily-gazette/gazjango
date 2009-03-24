from django.contrib import admin
from gazjango.seniors.models import SeniorListing

class SeniorAdmin(admin.ModelAdmin):
    list_display = ('senior', 'city', 'state', 'position')
    list_filter = ('position',)
    date_hierarchy = 'pub_date'
    prepopulated_fields = { 'slug': ('senior',) }
admin.site.register(SeniorListing, SeniorAdmin)