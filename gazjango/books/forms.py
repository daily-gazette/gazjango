from django import forms
from django.contrib.admin import widgets as admin_widgets

from gazjango.books.models    import BookListing
from gazjango.options.helpers import departments_taggroup
from gazjango.tagging.models  import Tag

# note that this form should be saved manually (with commit=False) and the
# author added to the new book
class SubmitBookForm(forms.ModelForm):
    departments = forms.MultipleChoiceField(
        widget=admin_widgets.FilteredSelectMultiple('departments', True),
        choices=[(tag.pk, tag.longest_name()) 
                 for tag in departments_taggroup().tags.all()]
    )
    
    class Meta:
        model = BookListing
        fields = ('title', 'departments', 'classes', 'cost',
                  'description', 'condition')
    
