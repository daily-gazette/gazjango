from django.contrib import admin
from gazjango.reviews.models import Establishment, Review

class EstablishmentAdmin(admin.ModelAdmin):
    prepopulated_fields = { 'slug': ('name',) }
    
    fieldsets = (
        (None, {
            'fields': ('name', 'establishment_type', 'access', 'phone', 'link', 'tags')
        }),
        ('Address', {
            'fields': ('street_address', 'city', 'zip_code')
        }),
        ('Advanced', {
            'classes': ('collapse',),
            'fields': ('slug', 'auto_geocode', 'latitude', 'longitude', 'other_info')
        }),
    )
    
    list_display = ('name', 'establishment_type')
    list_filter = ('name', 'establishment_type')
    
admin.site.register(Establishment, EstablishmentAdmin)


class ReviewAdmin(admin.ModelAdmin):
    list_display = ('slug', 'establishment')
    list_filter = ('slug', 'establishment')
admin.site.register(Review, ReviewAdmin)
