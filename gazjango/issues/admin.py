from django.contrib import admin
from gazjango.issues.models import Issue, WeatherJoke

class IssueAdmin(admin.ModelAdmin):
    pass
admin.site.register(Issue, IssueAdmin)

class WeatherJokeAdmin(admin.ModelAdmin):
    pass
admin.site.register(WeatherJoke, WeatherJokeAdmin)