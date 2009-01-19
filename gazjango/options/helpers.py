from gazjango.options.models import Option
from gazjango.tagging.models import TagGroup

def _option_getter(name, type, value):
    def _get_option():
        try:
            return Option.objects.get(name=name)
        except Option.DoesNotExist:
            opt = Option(name=name, type=type)
            opt.value = value() if callable(value) else value
            opt.save()
            return opt
    
    return _get_option

def _value_getter(option_getter):
    return lambda: option_getter().value()

def _value_setter(option_getter):
    def _set(value):
        opt = option_getter()
        opt.value = value
        opt.save()
        return opt
    
    return _set

def _make_option(name, type, value):
    opt_getter = _option_getter(name, type, value)
    return (_value_getter(opt_getter), _value_setter(opt_getter))


PUBLISHING_NAME = 'is_publishing'
is_publishing, set_publishing = _make_option(PUBLISHING_NAME, 'b', True)

NEW_USER_GROUPS_NAME = 'new_user_groups'
new_user_groups, set_new_user_groups = _make_option(NEW_USER_GROUPS_NAME, 'm', [])


DEPARTMENTS_TAGGROUP_NAME = 'Departments'
DEPARTMENTS_TAGGROUP_OPT_NAME = 'departments_taggroup_pk'
def _init_departments_taggroup():
    try:
        return TagGroup.objects.get(name=DEPARTMENTS_TAGGROUP_NAME)
    except TagGroup.DoesNotExist:
        from django.contrib.contenttypes.models import ContentType
        from gazjango.articles.models           import Article
        from gazjango.reviews.models            import Establishment
        
        group = TagGroup.objects.create(name=DEPARTMENTS_TAGGROUP_NAME)
        group.content_types = [ContentType.objects.get_for_model(Establishment),
                               ContentType.objects.get_for_model(Article)]
        group.save()
        return group

_departments_taggroup = _option_getter(DEPARTMENTS_TAGGROUP_OPT_NAME, 'f', 
                                       _init_departments_taggroup)
def departments_taggroup():
    value = _departments_taggroup().value
    if value:
        return value
    else:
        opt = set_departments_taggroup(_init_departments_taggroup())
        return opt.value

set_departments_taggroup = _value_setter(_departments_taggroup)
