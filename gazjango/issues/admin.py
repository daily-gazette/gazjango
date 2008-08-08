from django.contrib import admin
from models import Issue, IssueArticle, WeatherJoke

class IssueAdmin(admin.ModelAdmin):
    pass
admin.site.register(Issue, IssueAdmin)

class IssueArticleAdmin(admin.ModelAdmin):
    pass
admin.site.register(IssueArticle, IssueArticleAdmin)

class WeatherJokeAdmin(admin.ModelAdmin):
    pass
admin.site.register(WeatherJoke, WeatherJokeAdmin)