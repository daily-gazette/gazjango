from django.contrib import admin
from gazjango.options.models import Option

class OptionAdmin(admin.ModelAdmin):
    pass
admin.site.register(Option, OptionAdmin)

