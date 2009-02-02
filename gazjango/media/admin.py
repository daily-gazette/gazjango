from django.contrib import admin
from django         import forms
from gazjango.media.models import MediaFile, ImageFile, MediaBucket
from gazjango.misc.helpers import find_unique_name

class MediaBucketAdmin(admin.ModelAdmin):
    pass
admin.site.register(MediaBucket, MediaBucketAdmin)

class MediaFileAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'bucket')
    filter_horizontal = ('users',)
admin.site.register(MediaFile, MediaFileAdmin)


class ImageFileAdminForm(forms.ModelForm):
    class Meta:
        model = ImageFile
    
    description = forms.CharField(widget=forms.Textarea(attrs={'rows': 3, 'cols': 60}))
    
    def clean_slug(self):
        if self.cleaned_data['slug'] and self.cleaned_data['bucket']:
            self.cleaned_data['slug'] = find_unique_name(
                basename=self.cleaned_data['slug'],
                qset=self.cleaned_data['bucket'].imagefiles.all()
            )
        return self.cleaned_data['slug']
    

class ImageFileAdmin(admin.ModelAdmin):
    list_display = ('name', 'bucket', 'credit')#, 'admin_thumbnail_view')
    
    form = ImageFileAdminForm
    filter_horizontal = ('users',)
    fieldsets = (
        (None, {
            'fields': ('name', 'bucket', 'data', 'description')
        }),
        ('Authorship', {
            'fields': ('author_name', 'users', 'license_type', 'source_url')
        }),
        ('Manual Crops', {
            'fields': ('_front_data', '_issue_data', '_thumb_data'),
            'classes': ('collapse',),
        }),
        ('Advanced', {
            'fields': ('pub_date', 'slug'),
            'classes': ('collapse',),
        })
    )
    prepopulated_fields = { 'slug': ('name',) }
admin.site.register(ImageFile, ImageFileAdmin)

