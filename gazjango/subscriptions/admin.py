from django.contrib import admin
from gazjango.subscriptions.models import Subscriber

class SubscriberAdmin(admin.ModelAdmin):
    exclude = ('confirmation_key',)
    list_display = ('email', 'name', 'kind', 'receive', 'is_active', 'racy_content')
    list_filter = ('receive', 'racy_content')
    search_fields = ('_email', '_name', 'user__email', 'user__name')
admin.site.register(Subscriber, SubscriberAdmin)


