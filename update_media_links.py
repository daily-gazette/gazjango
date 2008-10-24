articles = MediaBucket.objects.get(slug='articles')
img_link = re.compile(r'^(img://)?([-\w]+)/([-.\w]+)$', re.IGNORECASE)

img_match = re.compile(r'''<(?P<tag>img)(?P<startattrs>[^>]*)\s+''' +
                       r'''src=(?P<qt>['"])(?P<src>[^'"]+)(?P=qt)''' +
                       r'''(?P<restattrs>[^>]*?)(?P<closed>\s*/?)\s*>''',
               re.IGNORECASE)
a_match   = re.compile(r'''<(?P<tag>a)(?P<startattrs>[^>]*)\s+''' +
                       r'''href\s*=\s*(?P<qt>['"])(?P<src>[^'"]+)(?P=qt)''' +
                       r'''(?P<restattrs>[^>]*?)(?P<closed>\s*/?)\s*>''',
               re.VERBOSE | re.IGNORECASE)

def subber(match):
    tag, startattrs, qt, src, restattrs, closed = match.groups()
    tag = tag.lower()
    
    src_name = 'src' if tag == 'img' else 'href'
    src_match = img_link.match(src)
    if not src_match:
        if not src.startswith('http://'):
            print "not matched: " + src
        return match.group(0)
    
    scheme, bucket, slug = src_match.groups()
    if tag == 'a' and not scheme:
        raise Exception('confusing link: ' + match)
    
    if MediaBucket.objects.filter(slug=bucket).count() == 0 or \
       MediaFile.objects.filter(slug=slug, bucket__slug=bucket).count() == 0:
        if MediaFile.objects.filter(slug=slug, bucket__pk=articles.pk).count():
            bucket = 'articles'
        else:
            raise Exception("unresolvable image link: " + match.group(0))
    
    d = match.groupdict()
    d['src'] = 'img://%s/%s' % (bucket, slug)
    return "<%(tag)s%(startattrs)s src=%(qt)s%(src)s%(qt)s%(restattrs)s%(closed)s>" % d


for article in Article.objects.all():
    article.text = re.sub(img_match, subber, article.text)
    article.text = re.sub(a_match, subber, article.text)
    article.save()
