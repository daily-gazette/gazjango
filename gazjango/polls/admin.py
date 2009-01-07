from django.contrib import admin
from gazjango.polls.models import Poll, PollOption

class PollOptionAdmin(admin.ModelAdmin):
    pass
admin.site.register(PollOption, PollOptionAdmin)

class PollOptionInline(admin.StackedInline):
    model = PollOption

class PollAdmin(admin.ModelAdmin):
    inlines = [PollOptionInline]
admin.site.register(Poll, PollAdmin)
