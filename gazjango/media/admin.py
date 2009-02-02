from django.contrib import admin
from gazjango.media.models import MediaFile, ImageFile, MediaBucket

class MediaBucketAdmin(admin.ModelAdmin):
    pass
admin.site.register(MediaBucket, MediaBucketAdmin)

class MediaFileAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'bucket')
    filter_horizontal = ('users',)
admin.site.register(MediaFile, MediaFileAdmin)

class ImageFileAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'bucket', 'get_admin_thumbnail')
    
    filter_horizontal = ('users',)
    fieldsets = {
        (None, {
            'fields': ('name', 'bucket', 'data')
        }),
        ('Authorship', {
            'fields': ('author_name', 'users', 'license_type', 'source_url')
        }),
        ('Manual Crops', {
            'fields': ('_front_data', '_issue_data', '_thumb_data'),
            'classes': ('collapse',),
        }),
        ('Advanced', {
            'fields': ('pub_date', 'description'),
            'classes': ('collapse',),
        })
    }
admin.site.register(ImageFile, ImageFileAdmin)

