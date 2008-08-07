from django.contrib import admin
from models import JobListing

class JobAdmin(admin.ModelAdmin):
    pass

admin.site.register(JobListing, JobAdmin)