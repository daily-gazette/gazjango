from django import forms
from django.utils.html import conditional_escape
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe
from django.forms.util import flatatt

from django.contrib.auth.models import User
from misc.helpers import get_jquery_path, get_static_path

def _author_link_for(username):
    u = User.objects.get(username=username)
    reps = { 'username': u.username, 'name': u.get_full_name() }
    return '<a href="#" id="author-%(username)s" onclick="return ' \
            '''removeAuthor('%(username)s');">%(name)s</a>''' % reps

class AuthorDisplayWidget(forms.Widget):
    def __init__(self, attrs=None):
        self.attrs = { 'id': 'authorsText' }
        if attrs:
            self.attrs.update(attrs)
    
    def render(self, name, value, attrs=None):
        if value is None: value = ''
        final_attrs = self.build_attrs(attrs, name=name)
        links = [_author_link_for(username) for username in value.split()]
        return u'<span%s>%s</span> (click to remove)<br/>' \
               % (flatatt(final_attrs), ' '.join(links))
    

class AuthorAddWidget(forms.TextInput):
    def __init__(self, *args, **kwargs):
        if ('attrs' not in kwargs) or (not kwargs['attrs']):
            kwargs['attrs'] = {}
        kwargs['attrs'].setdefault('size', 18)
        super(AuthorAddWidget, self).__init__(*args, **kwargs)
    
    def render(self, name, value, attrs=None):
        reg = super(AuthorAddWidget, self).render(name, value, attrs)
        link = u' <a href="#" onclick="return addAuthor()" id="addAuthor">' \
               u'add this author</a>'
        return mark_safe(reg + link)
    

class AuthorInputWidget(forms.MultiWidget):
    """
    An author-inputting widget, where you type in an author name in an
    autocompleting textbox to add it. Authors are listed as links in a
    <span> to the user, but really stored in a MultipleHiddenInput.
    """
    def __init__(self, display_attrs=None, add_attrs=None, hidden_attrs=None):
        widgets = (
            AuthorDisplayWidget(attrs=display_attrs),
            AuthorAddWidget(attrs=add_attrs),
            forms.HiddenInput(attrs=hidden_attrs),
        )
        super(AuthorInputWidget, self).__init__(widgets)
    
    def decompress(self, value):
        if value:
            return [value, None, value]
        return [None, None, None]
    
    def value_from_datadict(self, data, files, name):
        return self.widgets[2].value_from_datadict(data, files, name + '_2')
    
    class Media:
        js = (
            get_jquery_path(),
            get_static_path('js', 'jquery.autocomplete.js'),
            get_static_path('js', 'admin/authorField.js'),
        )
        css = {
            'all': (get_static_path('css', 'functions/autocomplete.css'),)
        }
    

class AuthorInputField(forms.MultipleChoiceField):
    default_error_messages = {
        'invalid_choice': "%(value)s is not a valid author name.",
        'invalid_list': "Select at least one author."
    }
    widget = AuthorInputWidget
    def __init__(self, *args, **kwargs):
        choices = User.objects.values_list('username', flat=True)
        super(AuthorInputField, self).__init__(choices, *args, **kwargs)
    
    def valid_value(self, value):
        return value in self.choices
    
    def clean(self, value):
        usernames = value.split()
        ps = []
        for n in usernames:
            try:
                ps.append(User.objects.get(username=n).get_profile())
            except User.DoesNotExist:
                raise forms.ValidationError('User "%s" does not exist.' % n)
            except UserProfile.DoesNotExist:
                raise forms.ValidationError("User '%s' doesn't have a profile." % n)
        return ps
    


class ForeignKeyField(forms.ChoiceField):
    def __init__(self, qset, show_field, *args, **kwargs):
        self.qset = qset
        if isinstance(show_field, (tuple, list)):
            cs = [(fields[0], reduce(lambda a,b: a or b, fields[1:]))
                   for fields in qset.values_list('pk', *show_field)]
        else:
            cs = [(pk, oth) for pk, oth in qset.values_list('pk', show_field)]
        super(ForeignKeyField, self).__init__(choices=cs, *args, **kwargs)
    
    def clean(self, value):
        try:
            return self.qset.get(pk=value)
        except self.qset.model.DoesNotExist:
            raise forms.ValidationError("Invalid choice.")
    
