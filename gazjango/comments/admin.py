from django.contrib import admin
from gazjango.comments.models import PublicComment

class PublicCommentAdmin(admin.ModelAdmin):
    list_display = ('article_name', 'number', 'display_name', 'is_anonymous', 'is_approved')
    list_display_links = ('number',)
    list_filter = ('is_approved',)
    search_fields = ('text', 'article__headline', 'name', 'email', 
                     'user__user__first_name', 'user__user__last_name', 'user__user__email')
admin.site.register(PublicComment, PublicCommentAdmin)
