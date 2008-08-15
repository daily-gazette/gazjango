from django.contrib import admin
from tagging.models import Tag, TaggedItem, TagGroup

admin.site.register(TaggedItem)
admin.site.register(Tag)
admin.site.register(TagGroup)
