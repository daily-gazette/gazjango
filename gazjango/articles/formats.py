def textile(text):
    import textile
    return textile.textile(text.encode('utf-8'), encoding="utf-8", output="utf-8")

def html(text):
    return text
