from django import forms
from django.contrib.localflavor.us.forms import USZipCodeField
from gazjango.reviews.models import Establishment

class SubmitEstablishmentForm(forms.ModelForm):
    zip_code = USZipCodeField()
    
    class Meta:
        model = Establishment
        fields = ('name', 'establishment_type', 'access', 
                  'street_address', 'city', 'zip_code',
                  'phone', 'link')
    
