from django.contrib import admin
from gazjango.issues.models import Issue, WeatherJoke

class IssueAdmin(admin.ModelAdmin):
    date_hierarchy = 'date'
    filter_horizontal = ('articles',)
admin.site.register(Issue, IssueAdmin)

class WeatherJokeAdmin(admin.ModelAdmin):
    date_hierarchy = 'date'
    list_display = ('date', 'line_one')
admin.site.register(WeatherJoke, WeatherJokeAdmin)