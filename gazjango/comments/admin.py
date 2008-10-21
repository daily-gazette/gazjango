from django.contrib import admin
from gazjango.comments.models import PublicComment

class PublicCommentAdmin(admin.ModelAdmin):
    list_display = ('article_name', 'number', 'display_name', 'is_anonymous', 'is_spam', 'is_approved')
    list_display_links = ('number',)
    list_filter = ('is_spam', 'is_approved')
admin.site.register(PublicComment, PublicCommentAdmin)
