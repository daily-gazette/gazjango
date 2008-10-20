from django.contrib import admin
from gazjango.comments.models import PublicComment

class PublicCommentAdmin(admin.ModelAdmin):
    pass
admin.site.register(PublicComment, PublicCommentAdmin)


