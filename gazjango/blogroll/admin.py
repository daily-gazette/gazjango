from django.contrib import admin

class OutsideSiteAdmin(admin.ModelAdmin):
    pass
admin.site.register(OutsideSite, OutsideSiteAdmin)

