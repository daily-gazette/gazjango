from django.db import models
from django.contrib.contenttypes.models import ContentType
import re

# booleans
FALSE_VALUES = set(['0', 'false', 'no', 'off'])
make_bool = lambda string: not (string.lower() in FALSE_VALUES)

# str lists
STR_LIST_SEP = '|'
STR_LIST_ESC = '\\'
UNESCAPED_STR_LIST_SEP = re.compile('(?<!%s)%s' % 
                         (re.escape(STR_LIST_ESC), re.escape(STR_LIST_SEP)))
ESCAPED_STR_LIST_SEP = re.compile(re.escape(STR_LIST_ESC) + re.escape(STR_LIST_SEP))

str_list_escape = lambda s: UNESCAPED_STR_LIST_SEP.sub(STR_LIST_ESC + STR_LIST_SEP, s)
str_list_unescape = lambda s: ESCAPED_STR_LIST_SEP.sub(STR_LIST_SEP, s)

def read_str_list(string):
    return [str_list_unescape(el) for el in string.split(STR_LIST_SEP)]

def render_str_list(strlist):
    return STR_LIST_SEP.join(str_list_escape(el) for el in strlist)


# many-fks -- stored as content_type_pk | pk1 | pk2 | ...
# only works with models where instance.pk==1 => model.objects.get(pk='1')==instance
class NotSameModel(Exception):
    pass

def read_manyfks(string):
    bits = read_str_list(string)
    if len(bits) < 2:
        return []
    model = ContentType.objects.get_for_id(bits[0]).model_class()
    return model._default_manager.in_bulk(bits[1:]).values()

def render_manyfks(instances):
    model = None # stick to straight iterable methods
    pks = []
    for instance in instances:
        if not model:
            model = instance.__class__
        elif instance.__class__ != model:
            raise NotSameModel
        pks.append(str(instance.pk))
    ct = str(ContentType.objects.get_for_model(model).pk)
    return render_str_list([ct] + pks)


# foreign keys: stored as content_type_pk | pk
def read_fk(string):
    try:
        return read_manyfks(string)[0]
    except IndexError:
        return None

def render_fk(instance):
    return render_manyfks([instance])

OPTION_TYPES = {
#   db    name       db->python,    python->db
    'b': ('boolean', make_bool,     str),
    's': ('string',  str,           str),
    'i': ('int',     int,           str),
    'f': ('float',   float,         str),
    'l': ('strlist', read_str_list, render_str_list),
    'm': ('manyfks', read_manyfks,  render_manyfks),
    'f': ('fk',      read_fk,       render_fk),
}
OPTION_CHOICES = [(db, name) for db, (name, dbtopy, pytodb) in OPTION_TYPES.items()]

format_from_db = lambda type, val: OPTION_TYPES[type][1](val)
format_for_db  = lambda type, val: OPTION_TYPES[type][2](val)

class Option(models.Model):
    name = models.CharField(max_length=100, unique=True, db_index=True)
    type = models.CharField(max_length=1, choices=OPTION_CHOICES)
    _value = models.CharField(blank=True, max_length=100)
    
    def _get_value(self):      return format_from_db(self.type, self._value)
    def _set_value(self, val): self._value = format_for_db(self.type, val)
    value = property(_get_value, _set_value)
    
    def __unicode__(self):
        return self.name
    
