from stories       import Article, ArticleRevision, Format
from sections      import Section, Subsection, Column
from specials      import Special, SpecialsCategory
from specials      import DummySpecialTarget, SectionSpecial
from concepts      import StoryConcept
from photo_spreads import PhotoSpread, PhotoInSpread
import tagging

try:
    tagging.register(Article)
except tagging.AlreadyRegistered:
    pass
