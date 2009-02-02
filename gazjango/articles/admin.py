from django.contrib import admin
from gazjango.articles.models import Article, Section, Subsection, Column, Writing
from gazjango.articles.models import StoryConcept, Special
from gazjango.articles.models import DummySpecialTarget, SectionSpecial
from gazjango.articles.models import PhotoSpread, PhotoInSpread


class WritingInline(admin.StackedInline):
    model = Writing
    verbose_name = "Author"
    verbose_name_plural = "Authors"
    extra = 1

class StoryAdmin(admin.ModelAdmin):
    date_hierarchy = 'pub_date'
    exclude = ('media', 'images')
    search_fields = ('headline', 'slug', 'text',)
    
    list_display = ('headline', 'status', 'author_names', 'pub_date', 'position', 'section', 'subsection')
    list_filter = ('status', 'position', 'possible_position', 'section', 'subsection')
    ordering = ('-pub_date',)
    
    inlines = [WritingInline]
admin.site.register(Article, StoryAdmin)


class PhotoInSpreadInline(admin.StackedInline):
    model = PhotoInSpread
    extra = 3

class PhotoSpreadAdmin(admin.ModelAdmin):
    inlines = [PhotoInSpreadInline, WritingInline]
    list_display = ('headline', 'status', 'author_names', 'position', 'section', 'subsection')
    exclude = ('media', 'images', 'text')
    
admin.site.register(PhotoSpread, PhotoSpreadAdmin)





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
    filter_horizontal = ('users',)
    list_display = ('name', 'due', 'status', 'user_names')
    list_filter = ('due', 'status')
admin.site.register(StoryConcept, StoryConceptAdmin)


class SpecialsAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'date')
    list_filter = ('category',)
admin.site.register(Special, SpecialsAdmin)


class DummySpecialTargetAdmin(admin.ModelAdmin):
    pass
admin.site.register(DummySpecialTarget, DummySpecialTargetAdmin)


class SectionSpecialsAdmin(admin.ModelAdmin):
    pass
admin.site.register(SectionSpecial, SectionSpecialsAdmin)
