from django import forms
from django.contrib.localflavor.us.forms import USZipCodeField
from gazjango.reviews.models import Establishment, Review

class SubmitEstablishmentForm(forms.ModelForm):
    zip_code = USZipCodeField()
    
    class Meta:
        model = Establishment
        fields = ('name', 'establishment_type', 'access', 
                  'street_address', 'city', 'zip_code',
                  'phone', 'link')
    

class SubmitReviewForm(forms.Form):
    cost = forms.ChoiceField(choices=Review.COST_CHOICES, required=True)
    rating = forms.ChoiceField(choices=Review.RATING_CHOICES, required=True)
    text = forms.CharField(widget=forms.Textarea(attrs={'cols': 65}), required=True)
