def textile(text):
    from gazjango.misc.textile import textile
    return textile(text.encode('utf-8'), encoding="utf-8", output="utf-8")

def html(text):
    return text


FORMATS = {
    'h': ('Raw HTML', html),
    't': ('Textile',  textile),
}
FORMAT_CHOICES = [(k, v[0]) for k, v in FORMATS.items()]
FORMAT_FUNCS   = dict((k, v[1]) for k, v in FORMATS.items())