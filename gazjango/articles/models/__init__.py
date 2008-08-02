from stories       import Article, ArticleRevision, Format
from sections      import Section, Subsection
from specials      import Special, SpecialsCategory, DummySpecialTarget
from concepts      import StoryConcept
from photo_spreads import PhotoSpread, PhotoInSpread
import tagging

try:
    tagging.register(Article)
except tagging.AlreadyRegistered:
    pass
