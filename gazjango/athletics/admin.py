from django.contrib import admin
from gazjango.athletics.models import Team, Game

class TeamAdmin(admin.ModelAdmin):
    list_display = ('sport', 'gender', 'trimester')
    list_filter  = ('sport', 'gender', 'trimester')
admin.site.register(Team, TeamAdmin)

class GameAdmin(admin.ModelAdmin):
    list_display = ('date', 'team', 'opponent', 'outcome', 'rank', 'home')
    list_filter  = ('date', 'team', 'opponent', 'outcome')
admin.site.register(Game, GameAdmin)
