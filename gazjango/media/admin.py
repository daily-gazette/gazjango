from django.contrib import admin
from models import MediaFile, ImageFile, MediaBucket

class MediaBucketAdmin(admin.ModelAdmin):
    pass
admin.site.register(MediaBucket, MediaBucketAdmin)

class MediaFileAdmin(admin.ModelAdmin):
    pass
admin.site.register(MediaFile, MediaFileAdmin)

class ImageFileAdmin(admin.ModelAdmin):
    pass
admin.site.register(ImageFile, ImageFileAdmin)

