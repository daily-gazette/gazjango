from django import forms
from django.contrib.admin import widgets as admin_widgets

from gazjango.screw.models    import ScrewListing

# note that this form should be saved manually (with commit=False)
class SubmitScreweeForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        needs_email = kwargs.pop('needs_email', False)
        super(SubmitScreweeForm, self).__init__(*args, **kwargs)
        if needs_email:
            self.fields['email'] = forms.EmailField()
    
    class Meta:
        model = ScrewListing
        fields = ('screwer', 'year')
    
