from gazjango.popular.models import StoryRank
from django.contrib import admin

class StoryRankAdmin(admin.ModelAdmin):
    list_display = ('article', 'hits','last_update',)

admin.site.register(StoryRank, StoryRankAdmin)