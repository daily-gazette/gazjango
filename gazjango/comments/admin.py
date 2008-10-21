from django.contrib import admin
from gazjango.comments.models import PublicComment

class PublicCommentAdmin(admin.ModelAdmin):
    list_display = ('subject', 'display_name', 'is_anonymous', 'is_spam', 'is_approved')
    list_filter = ('is_spam', 'is_approved')
admin.site.register(PublicComment, PublicCommentAdmin)
