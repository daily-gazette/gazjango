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
        choices = self._find_choices()
        super(AuthorInputField, self).__init__(choices, *args, **kwargs)
    
    def _find_choices(self):
        return User.objects.values_list('username', flat=True)
    
    def refresh_choices(self):
        self.choices = self._find_choices()
    
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
    

def _first(lst):
    reduce(lambda a, b: a or b, lst)

class ForeignKeyField(forms.ChoiceField):
    def _find_choices(self):
        return [(fields[0], _first(fields[1:])) for fields
                in self.model.objects.values_list('pk', *self.show_field)]
    
    def __init__(self, model, show_field, *args, **kwargs):
        self.model = model
        if isinstance(show_field, (tuple, list)):
            self.show_field = show_field
        else:
            self.show_field = (show_field,)
        
        kwargs['choices'] = self._find_choices()
        super(ForeignKeyField, self).__init__(*args, **kwargs)
    
    def refresh_choices(self):
        self.choices = self._find_choices()
    
    def clean(self, value):
        try:
            return self.model.objects.get(pk=value)
        except self.model.DoesNotExist:
            raise forms.ValidationError('Invalid choice "%s".' % value)
    

# multiple inheritance is confusing, so we're going to avoid it
class MultipleForeignKeyField(forms.MultipleChoiceField):
    def __init__(self, model, display_field, group=None, group_label_field=None,
                 *args, **kwargs):
        self.model = model
        if isinstance(display_field, (tuple, list)):
            self.display_field = display_field
        else:
            self.display_field = (display_field,)
        self.group = group
        self.group_label_field = group_label_field
        
        kwargs['choices'] = self._find_choices()
        super(MultipleForeignKeyField, self).__init__(*args, **kwargs)
    
    def _find_choices(self):
        if self.group:
            # how to label groups
            if self.group_label_field:
                label = lambda x: \
                         x.__getattribute__(self.group_label_field) if x else x
            else:
                label = lambda x: unicode(x) if x else x
            
            # how to show each model
            def show(instance):
                for field in self.display_field:
                    if instance.__dict__[field]:
                        return instance.__dict__[field]
                return unicode(instance)
            
            # organize into {label: [(pk, name), (pk, name), ...]}
            results = {}
            for instance in self.model.objects.all():
                grp = label(instance.__getattribute__(self.group))
                results.setdefault(grp, []).append((instance.pk, show(instance)))
            
            # dict => list
            choices = results.items()
            
            # sort the groups
            choices.sort(key=lambda lst: lst[0])
            if len(choices) and choices[0][0] is None:
                choices.append( ('Other', choices.pop(0)[1]) )
            
            # sort within each group
            second_lower = lambda pair: pair[1].lower()
            for label, items in choices:
                items.sort(key=second_lower)
            
            return choices
        
        else:
            return [(fields[0], _first(fields[1:])) for fields
                    in self.model.objects.values_list('pk', *self.display_field)]
    
    def refresh_choices(self):
        self.choices = self._find_choices()
    
    def clean(self, value):
        def get_or_raise(pk):
            try:
                return self.model.objects.get(pk=pk)
            except self.model.DoesNotExist:
                raise forms.ValidationError('Invalid choice "%s".' % pk)
        return [get_or_raise(pk) for pk in value]
    
