from django.contrib import admin
from gazjango.athletics.models import Team, Game

class TeamAdmin(admin.ModelAdmin):
    list_display = ('sport', 'gender', 'trimester')
    list_filter  = ('sport', 'gender', 'trimester')
admin.site.register(Team, TeamAdmin)

class GameAdmin(admin.ModelAdmin):
    list_display = ('team', 'opponent', 'outcome', 'rank')
    list_filter  = ('team', 'opponent', 'outcome', 'rank')
admin.site.register(Game, GameAdmin)
