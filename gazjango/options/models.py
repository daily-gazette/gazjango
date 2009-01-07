from django.db import models

FALSE_VALUES = set(['0', 'false', 'no', 'off'])
def make_bool(string):
    return not (string.lower() in FALSE_VALUES)

OPTION_TYPES = {
#   db    name       db->python, python->db
    'b': ('boolean', make_bool,  str),
    's': ('string',  str,        str),
    'i': ('int',     int,        str),
    'f': ('float',   float,      str),
}
OPTION_CHOICES = [(db, name) for db, (name, dbtopy, pytodb) in OPTION_TYPES.items()]

format_from_db = lambda type, val: OPTION_TYPES[type][1](val)
format_for_db  = lambda type, val: OPTION_TYPES[type][2](val)

class Option(models.Model):
    name = models.CharField(max_length=100, unique=True)
    type = models.CharField(max_length=1, choices=OPTION_CHOICES)
    _value = models.CharField(blank=True, max_length=100)
    
    def _get_value(self):      return format_from_db(self.type, self._value)
    def _set_value(self, val): self._value = format_for_db(self.type, val)
    value = property(_get_value, _set_value)
    
    def __unicode__(self):
        return self.name
    
