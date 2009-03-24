from django import forms
from django.contrib.admin import widgets as admin_widgets

from gazjango.seniors.models    import SeniorListing

# note that this form should be saved manually (with commit=False)
class SubmitSeniorForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        needs_email = kwargs.pop('needs_email', False)
        super(SubmitSeniorForm, self).__init__(*args, **kwargs)
        if needs_email:
            self.fields['email'] = forms.EmailField()
    
    class Meta:
        model = SeniorListing
        fields = ('city','state','position','movein-month','movein-year','moveout-month','moveout-year')
    
