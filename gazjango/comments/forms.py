from django import forms

def make_comment_form(data=None, logged_in=False, **kwargs):
    if data:
        form = CommentForm(data, **kwargs)
    else:
        form = CommentForm(**kwargs)
    if logged_in:
        # javascript does its magic with anonymous
        form.fields['name'].widget = forms.TextInput()
        
        form.fields['email'].widget = forms.HiddenInput()
        form.fields['email'].required = False
    else:
        form.fields['anonymous'].widget.attrs['display'] = 'none'
        form.fields['anonymous'].initial = True
        
        form.fields['name'].required = True
        # NOTE: temporary, until we get the error handling better
        form.fields['email'].required = False
    return form

class CommentForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea(attrs={'rows': 8, 'cols': 52}))
    
    anonymous = forms.BooleanField(widget=forms.CheckboxInput(), initial=False, required=False)
    name = forms.CharField(max_length=100, required=False)
    email = forms.EmailField()
