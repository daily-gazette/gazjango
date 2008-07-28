from django import forms

class BaseCommentForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea(attrs={'rows': 8, 'cols': 52}))

class AnonCommentForm(BaseCommentForm):
    name  = forms.CharField(max_length=100)
    email = forms.EmailField()

class UserCommentForm(BaseCommentForm):
    anonymous = forms.BooleanField(widget=forms.CheckboxInput(
                    attrs={'onclick': 'toggleNameDisabled()'}))
    name = forms.CharField(widget=forms.TextInput(
                    attrs={'id': 'filled-name', 'disabled': True}))
