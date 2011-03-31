from django.contrib import admin
from gazjango.housing.models import HousingListing

class SeniorAdmin(admin.ModelAdmin):
    list_display = ('student', 'city', 'state', 'position')
    list_filter = ('position',)
    date_hierarchy = 'pub_date'
    prepopulated_fields = { 'slug': ('student',) }

    actions = ['unpublish']

    def make_published(self, request, queryset):
        queryset.update(is_published=False)
    make_published.short_description = "Remove selected listings from the website"

admin.site.register(HousingListing, SeniorAdmin)