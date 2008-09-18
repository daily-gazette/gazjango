from django import forms
from gazjango.jobs.models import JobListing

class SubmitJobForm(forms.ModelForm):
    description = forms.CharField(widget=forms.Textarea(attrs={'rows': 5, 'cols': 40}))
    
    is_paid = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={'onchange': 'togglePay();'}),
        initial=False,
        required=False
    )
    
    class Meta:
        model = JobListing
        fields  = ('name', 'description', 'is_paid', 'pay')
        fields += ('hours', 'when', 'where', 'at_swat', 'needs_car')
    
