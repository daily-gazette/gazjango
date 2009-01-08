from django.contrib import admin
from gazjango.tagging.models import Tag, TagGroup

class TagAdmin(admin.ModelAdmin):
    pass
admin.site.register(Tag, TagAdmin)

class TagGroupAdmin(admin.ModelAdmin):
    pass
admin.site.register(TagGroup, TagGroupAdmin)

