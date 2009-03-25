from django.contrib import admin
from gazjango.housing.models import HousingListing

class SeniorAdmin(admin.ModelAdmin):
    list_display = ('student', 'city', 'state', 'position')
    list_filter = ('position',)
    date_hierarchy = 'pub_date'
    prepopulated_fields = { 'slug': ('senior',) }
admin.site.register(HousingListing, SeniorAdmin)