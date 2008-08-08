from django.contrib import admin
from models import Poll, Option

class OptionAdmin(admin.ModelAdmin):
    pass
admin.site.register(Option, OptionAdmin)

class OptionInline(admin.StackedInline):
    model = Option

class PollAdmin(admin.ModelAdmin):
    inlines = [OptionInline]
admin.site.register(Poll, PollAdmin)
