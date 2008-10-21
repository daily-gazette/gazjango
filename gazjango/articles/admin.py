from django.contrib import admin
from gazjango.articles.models import Article, Section, Subsection, Column, Writing
from gazjango.articles.models import StoryConcept, Special, DummySpecialTarget
from gazjango.articles.models import SpecialsCategory, SectionSpecial


class WritingInline(admin.StackedInline):
    model = Writing
    verbose_name = "Author"
    verbose_name_plural = "Authors"

class StoryAdmin(admin.ModelAdmin):
    date_hierarchy = 'pub_date'
    exclude = ('media', )
    search_fields = ('headline', 'slug', 'text',)
    
    list_display = ('headline', 'status', 'author_names', 'position', 'possible_position', 'is_racy')
    list_filter = ('status', 'position', 'possible_position')
    
    inlines = WritingInline
admin.site.register(Article, StoryAdmin)


class SectionAdmin(admin.ModelAdmin):
    pass
admin.site.register(Section, SectionAdmin)

class SubsectionAdmin(admin.ModelAdmin):
    pass
admin.site.register(Subsection, SubsectionAdmin)

class ColumnAdmin(admin.ModelAdmin):
    pass
admin.site.register(Column, ColumnAdmin)

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
