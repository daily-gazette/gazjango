from django import forms
from django.contrib.auth.models import User


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
    
