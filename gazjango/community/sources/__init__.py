from django.conf import settings
import logging

log = logging.getLogger('community.sources')

try:
    import xml.etree.cElementTree as element_tree
except ImportError:
    try:
        import elementtree.ElementTree as element_tree
    except ImportError:
        try:
            import cElementTree as element_tree
        except ImportError:
            raise ImportError("No ElementTree found")
log.debug("Using specified etree module: %s" % element_tree)

def import_source_modules(source_list=settings.AGRO_SETTINGS['source_list'], class_name=''):
    sources = []
    for source in source_list:
        log.debug('trying to load %s' % source)
        try:
            # CHANGED: make sure this works :)
            sources.append(__import__("community.sources.%s" % source))
        except ImportError as e:
            log.error('unable to load %s: %s', source, e)
    return sources
