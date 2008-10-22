from django.contrib import admin
from gazjango.jobs.models import JobListing

class JobAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_published', 'pub_date', 'contact_name', 'is_filled')
    list_filter = ('is_published', 'is_filled')
    date_hierarchy = 'pub_date'
admin.site.register(JobListing, JobAdmin)
