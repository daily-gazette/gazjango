from django import forms
from django.contrib.admin import widgets as admin_widgets
from django.contrib.auth.models import User

from gazjango.articles.models      import StoryConcept
from gazjango.accounts.models      import UserProfile


# note that this form should be saved manually (with commit=False)
class SubmitStoryConcept(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super(SubmitStoryConcept, self).__init__(*args, **kwargs)
    
    class Meta:
        model = StoryConcept
        fields = ('name','due')
    
class ConceptSaveForm(forms.Form):        
    name  = forms.CharField(label = 'Concept',   widget=forms.HiddenInput(attrs={'size': 30}), required=True)
    due   = forms.CharField(label = 'Due Date',  widget=forms.TextInput(attrs={'size': 15}),   required=False)
    users = forms.ModelMultipleChoiceField(label = 'Users', queryset=User.objects.all(), widget=admin_widgets.FilteredSelectMultiple('Users', False), required=False)