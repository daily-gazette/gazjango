from django.contrib import admin
from gazjango.subscriptions.models import Subscriber

class SubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'name', 'kind', 'receive', 'is_active', 'racy_content')
    list_filter = ('receive', 'racy_content')
    search_fields = ('_email', 'user__user__email',
                     '_name', 'user__user__first_name', 'user__user__last_name')
admin.site.register(Subscriber, SubscriberAdmin)


