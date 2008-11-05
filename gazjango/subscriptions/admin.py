from django.contrib import admin
from gazjango.subscriptions.models import Subscriber

class SubscriberAdmin(admin.ModelAdmin):
    exclude = ('confirmation_key',)
    list_display = ('email', 'name', 'receive')
    list_filter = ('receive',)
admin.site.register(Subscriber, SubscriberAdmin)


