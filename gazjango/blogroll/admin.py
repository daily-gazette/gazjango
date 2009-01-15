from django.contrib import admin
from gazjango.blogroll.models import OutsideSite

class OutsideSiteAdmin(admin.ModelAdmin):
    pass
admin.site.register(OutsideSite, OutsideSiteAdmin)

