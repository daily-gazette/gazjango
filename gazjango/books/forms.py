from django import forms
from django.contrib.admin import widgets as admin_widgets

from gazjango.books.models    import BookListing
from gazjango.options.helpers import departments_taggroup
from gazjango.tagging.models  import Tag

# note that this form should be saved manually (with commit=False) and the
# author added to the new book
class SubmitBookForm(forms.ModelForm):
    departments = forms.MultipleChoiceField(
        widget=admin_widgets.FilteredSelectMultiple('departments', False),
        required=False
    )
    
    def __init__(self, *args, **kwargs):
        needs_email = kwargs.pop('needs_email', False)
        super(SubmitBookForm, self).__init__(*args, **kwargs)
        self.fields['departments'].choices = [
            (tag.pk, tag.longest_name())
            for tag in departments_taggroup().tags.all()
        ]
        if needs_email:
            self.fields['email'] = forms.EmailField()
    
    def clean_cost(self):
        if '$' not in self.cleaned_data['cost']:
            self.cleaned_data['cost'] = '$' + self.cleaned_data['cost']
        return self.cleaned_data['cost']
    
    class Meta:
        model = BookListing
        fields = ('title', 'departments', 'classes', 'cost',
                  'description', 'condition')
    
