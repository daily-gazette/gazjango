from django.contrib import admin
from gazjango.subscriptions.models import Subscriber

class SubscriberAdmin(admin.ModelAdmin):
    exclude = ('confirmation_key',)
admin.site.register(Subscriber, SubscriberAdmin)


