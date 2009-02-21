from django import forms
from django.newforms import form_for_model
from gazjango.articles.models      import StoryConcept

# note that this form should be saved manually (with commit=False)
class SubmitStoryConcept(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super(SubmitStoryConcept, self).__init__(*args, **kwargs)
    
    class Meta:
        model = StoryConcept
        fields = ('name', 'notes','due')
    
