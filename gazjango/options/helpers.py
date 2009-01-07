from gazjango.options.models import Option

PUBLISHING_NAME = 'is_publishing'
def _publishing_option():
    d = dict(type='b', _value='1')
    return Option.objects.get_or_create(name=PUBLISHING_NAME, defaults=d)[0]

def is_publishing():        
    return _publishing_option().value

def set_publishing(val):
    opt = _publishing_option()
    opt.value = val
    opt.save()
