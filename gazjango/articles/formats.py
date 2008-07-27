def textile(text):
    from misc.textile import textile
    return textile(text.encode('utf-8'), encoding="utf-8", output="utf-8")

def html(text):
    return text
