from django.contrib import admin
from gazjango.articles.models import Article, Section, Subsection, StoryConcept, Special
from gazjango.articles.models import Special, DummySpecialTarget, SpecialsCategory, SectionSpecial

class StoryAdmin(admin.ModelAdmin):
    filter_horizontal = ("subsections",)
admin.site.register(Article, StoryAdmin)


class SectionAdmin(admin.ModelAdmin):
    pass
admin.site.register(Section, SectionAdmin)


class StoryConceptAdmin(admin.ModelAdmin):
    pass
admin.site.register(StoryConcept, StoryConceptAdmin)


class SpecialsAdmin(admin.ModelAdmin):
    pass
admin.site.register(Special, SpecialsAdmin)


class SpecialsCategoryAdmin(admin.ModelAdmin):
    pass
admin.site.register(SpecialsCategory, SpecialsCategoryAdmin)


class DummySpecialTargetAdmin(admin.ModelAdmin):
    pass
admin.site.register(DummySpecialTarget, DummySpecialTargetAdmin)


class SectionSpecialsAdmin(admin.ModelAdmin):
    pass
admin.site.register(SectionSpecial, SectionSpecialsAdmin)
