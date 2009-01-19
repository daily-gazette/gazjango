reps = {
    'year':  r'(?P<year>\d{4})',
    'month': r'(?P<month>\d{1,2})',
    'day':   r'(?P<day>\d{1,2})',
    
    'slug': r'(?P<slug>[-\w]+)',
    'name': r'(?P<name>[-\w]+)',
    'kind': r'(?P<kind>[-\w]+)',
    'bucket':     r'(?P<bucket>[-\w]+)',
    'section':    r'(?P<section>[a-zA-Z][-\w]+)',
    'subsection': r'(?P<subsection>[a-zA-Z][-\w]+)',
    
    'num': r'(?P<num>\d+)',
    'uid': r'(?P<uidb36>[a-z0-9]+)',
    'token': r'(?P<token>\w+-\w+)',
}
