from django import forms
from media.models import MediaFile, ImageFile, MediaBucket
from misc.forms import AuthorInputField, ForeignKeyField

class MediaForm(forms.ModelForm):
    class Meta:
        model = MediaFile
    

class ImageForm(forms.Form):
    data   = forms.ImageField(label="Image")
    shape  = forms.ChoiceField(choices=ImageFile.SHAPE_CHOICES)
    
    name   = forms.CharField(max_length=100, min_length=3)
    slug   = forms.RegexField(max_length=40, min_length=3, regex=r'[-\w]+')
    
    bucket = ForeignKeyField(MediaBucket.objects, ('name', 'slug'))
    
    authors = AuthorInputField(required=False, help_text="Optional: if somebody Swarthmore-related made the image, add them as an author; don't create accounts for random internet people, though.")
    
    description = forms.CharField(widget=forms.Textarea(attrs={'rows': '3', 'cols': '40'}), required=False, help_text="Optional: describe the image. Will be the default (but overridable) caption when added to an article.")
    
    license = forms.CharField(widget=forms.Textarea(attrs={'rows': '3', 'cols': '40'}), required=False, help_text="Optional: if you didn't make the image, say who did, and why you're allowed to use it. (Is it Creative Commons?)")
    
    def clean(self):
        bucket = self.cleaned_data['bucket']
        slug   = self.cleaned_data['slug']
        if bucket and slug:
            if MediaFile.objects.filter(bucket=bucket, slug=slug).count() > 0:
                raise forms.ValidationError(
                    "Bucket '%s' already has a file with slug '%s'." \
                    % (bucket.name or bucket.slug, slug)
                )
        return self.cleaned_data
    

class BucketForm(forms.ModelForm):
    class Meta:
        model = MediaBucket
    
