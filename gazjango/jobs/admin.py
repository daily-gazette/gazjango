from django.contrib import admin
from gazjango.jobs.models import JobListing

class JobAdmin(admin.ModelAdmin):
    pass
admin.site.register(JobListing, JobAdmin)
