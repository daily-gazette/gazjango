from django import forms

def make_comment_form(data=None, logged_in=False, **kwargs):
    if data:
        form = CommentForm(data, **kwargs)
    else:
        form = CommentForm(**kwargs)
    if logged_in:
        form.fields['name'].widget = forms.TextInput(
            attrs={ 'id': 'filled-name', 'disabled': True }
        )
        
        form.fields['email'].widget = forms.HiddenInput()
        form.fields['email'].required = False
        
        form.fields['anonymous'].widget = forms.CheckboxInput(
            attrs={ 'onclick': 'toggleNameDisabled();' }
        )
    else:
        form.fields['anonymous'].widget = forms.CheckboxInput(
            attrs={ 'display': 'none' }
        )
        form.fields['anonymous'].initial = True
    return form

class CommentForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea(attrs={'rows': 8, 'cols': 52}))
    
    anonymous = forms.BooleanField(widget=forms.HiddenInput())
    name = forms.CharField(max_length=100)
    email = forms.EmailField()
