from django.contrib import admin
from gazjango.reviews.models import Establishment, Review

class EstablishmentAdmin(admin.ModelAdmin):
    prepopulated_fields = { 'slug': ('name',) }
    
    fieldsets = (
        (None, {
            'fields': ('name', 'establishment_type', 'tags', 'is_published')
        }),
        ('Address', {
            'fields': ('street_address', 'city', 'zip_code', 'access')
        }),
        ('Extra Info', {
            'classes': ('collapse',),
            'fields': ('phone', 'link', 'other_info')
        }),
        ('Advanced', {
            'classes': ('collapse',),
            'fields': ( 
                       'auto_geocode', 'latitude', 'longitude',
                       'auto_nearest_station', '_nearest_station')
        }),
    )
    filter_horizontal = ('tags',)
    
    list_display = ('name', 'establishment_type', 'city', 'tag_names', 'is_published')
    list_filter = ('establishment_type', 'access')
    
admin.site.register(Establishment, EstablishmentAdmin)


class ReviewAdmin(admin.ModelAdmin):
    list_display = ('reviewer', 'establishment')
    list_filter = ('establishment',)
admin.site.register(Review, ReviewAdmin)
