from gazjango.options.models import Option

def _make_option(name, type, _value):
    def _get_option():
        d = dict(type=type, _value=_value)
        return Option.objects.get_or_create(name=name, defaults=d)[0]
    
    get_val = lambda: _get_option().value
    def set_val(val):
        opt = _get_option()
        opt.value = val
        opt.save()
    
    return (get_val, set_val)


PUBLISHING_NAME = 'is_publishing'
is_publishing, set_publishing = _make_option(PUBLISHING_NAME, 'b', '1')

NEW_USER_GROUPS_NAME = 'new_user_groups'
new_user_groups, set_new_user_groups = _make_option(NEW_USER_GROUPS_NAME, 'm', '')
