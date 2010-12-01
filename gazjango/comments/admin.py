from django.contrib import admin
from gazjango.comments.models import PublicComment



class PublicCommentAdmin(admin.ModelAdmin):
    date_hierarchy = 'time'
    list_display = ('article_name', 'number', 'display_name', 'user_or_email',
                    'is_approved', 'superhidden', 'time')
    list_display_links = ('number',)
    list_filter = ('is_approved', 'superhidden')
    search_fields = ('text', 'article__headline', 'name', 'email', 
                     'user__user__first_name', 'user__user__last_name', 'user__user__email')

    actions = ['mark_as_spam', 'approve']

    def mark_as_spam(self, request, queryset):
        counter = 0
        for comment in queryset:
            comment.mark_as_spam()
            counter += 1
        self.message_user(request, "%s comments were successfully spammed" % counter)
    mark_as_spam.short_description = "Mark selected comments as spam (deletes them too)"

    def approve(self, request, queryset):
        rows_updated = queryset.update(is_approved=True)
        if rows_updated == 1:
            message_bit = "1 comment was"
        else:
            message_bit = "%s comments were" % rows_updated
        self.message_user(request, message_bit + " were successfully approved.")
    approve.short_description = "Approve selected comments"

admin.site.register(PublicComment, PublicCommentAdmin)
