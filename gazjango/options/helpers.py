from django.contrib.contenttypes.models import ContentType

from gazjango.articles.models import Article
from gazjango.options.models  import Option
from gazjango.reviews.models  import Establishment
from gazjango.tagging.models  import TagGroup

def _make_option(name, type, value):
    def _get_option():
        try:
            return Option.objects.get(name=name)
        except Option.DoesNotExist:
            opt = Option.objects.create(name=name, type=type)
            opt.value = value() if callable(value) else value
    
    get_val = lambda: _get_option().value
    def set_val(val):
        opt = _get_option()
        opt.value = val
        opt.save()
    
    return (get_val, set_val)


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
        group = TagGroup.objects.create(name=DEPARTMENTS_TAGGROUP_NAME)
        group.content_types = [ContentType.objects.get_for_model(Establishment),
                               ContentType.objects.get_for_model(Article)]
        group.save()
        return group

departments_taggroup, set_departments_taggroup = \
    _make_option(DEPARTMENTS_TAGGROUP_OPT_NAME, 'f', _init_departments_taggroup)
