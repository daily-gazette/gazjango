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
    list_display = ('name', 'slug', 'bucket')
    filter_horizontal = ('users',)
admin.site.register(ImageFile, ImageFileAdmin)

