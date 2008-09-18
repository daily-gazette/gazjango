from gazjango.articles.models.stories       import Article, ArticleRevision, Format
from gazjango.articles.models.sections      import Section, Subsection, Column
from gazjango.articles.models.specials      import Special, SpecialsCategory
from gazjango.articles.models.specials      import DummySpecialTarget, SectionSpecial
from gazjango.articles.models.concepts      import StoryConcept
from gazjango.articles.models.photo_spreads import PhotoSpread, PhotoInSpread
from gazjango import tagging

try:
    tagging.register(Article)
except tagging.AlreadyRegistered:
    pass
