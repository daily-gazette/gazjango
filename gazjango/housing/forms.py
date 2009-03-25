from django import forms
from django.contrib.admin import widgets as admin_widgets

from gazjango.housing.models    import HousingListing

# note that this form should be saved manually (with commit=False)
class SubmitHousingForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        needs_email = kwargs.pop('needs_email', False)
        super(SubmitHousingForm, self).__init__(*args, **kwargs)
        if needs_email:
            self.fields['email'] = forms.EmailField()
        if needs_name:
            self.fields['name'] = forms.CharField(max_length=40)
    
    class Meta:
        model = HousingListing
        fields = ('city','state','position','moveinmonth','moveinyear','moveoutmonth','moveoutyear','notes')
    
