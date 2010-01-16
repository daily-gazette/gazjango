from django.contrib import admin
from django import forms
from gazjango.articles.models import Article, Section, Subsection, Column, Writing
from gazjango.articles.models import StoryConcept, Special
from gazjango.articles.models import DummySpecialTarget, SectionSpecial
from gazjango.articles.models import PhotoSpread, PhotoInSpread

_help_text = lambda field, model=Article: model._meta.get_field_by_name(field)[0].help_text
_blank = lambda field, model=Article: model._meta.get_field_by_name(field)[0].blank
args = lambda *a, **kw: {'help_text': _help_text(*a, **kw), 'required': not _blank(*a, **kw)}

class StoryAdminForm(forms.ModelForm):
    class Meta:
        model = Article
    
    headline = forms.CharField(
        widget=forms.TextInput(attrs={'size': '80'}),
        **args('headline'))
    short_title = forms.CharField(
        widget=forms.TextInput(attrs={'size': 50, 'maxchars': 40}),
        **args('short_title'))
    text = forms.CharField(
        widget=forms.Textarea(attrs={'rows': '40', 'cols': '120'}),
        **args('text'))
    short_summary = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 2, 'cols': 100}),
        **args('short_summary'))

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
    list_filter = ('status', 'position', 'section', 'subsection')
    ordering = ('-pub_date',)
    
    form = StoryAdminForm
    fieldsets = (
        (None, {
            'fields': ('headline', 'short_title', 'slug',
                       'status', 'concept', 'text', 'main_image')
        }),
        ('Summaries', {
            'fields': ('short_summary', 'summary'),
        }),
        ('Placement', {
            'fields': ('section', 'subsection', 'position'),
        }),
        ('Advanced', {
            'fields': ('pub_date', 'format', 'is_racy', 'comments_allowed'),
            'classes': ('collapse',),
        }),
    )
    
    inlines = [WritingInline]
admin.site.register(Article, StoryAdmin)

class PhotoInSpreadInline(admin.StackedInline):
    model = PhotoInSpread
    extra = 3

class PhotoSpreadAdmin(admin.ModelAdmin):
    inlines = [PhotoInSpreadInline, WritingInline]
    list_display = ('headline', 'status', 'author_names', 'position', 'section', 'subsection')
    exclude = ('media', 'images')
    
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
