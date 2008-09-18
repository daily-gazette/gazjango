from django.contrib import admin
from gazjango.accounts.models import UserKind, ContactMethod, ContactItem
from gazjango.accounts.models import UserProfile, Position, Holding

class UserKindAdmin(admin.ModelAdmin):
    pass
admin.site.register(UserKind, UserKindAdmin)

class ContactMethodAdmin(admin.ModelAdmin):
    pass
admin.site.register(ContactMethod, ContactMethodAdmin)

class ContactItemAdmin(admin.ModelAdmin):
    pass
admin.site.register(ContactItem, ContactItemAdmin)

class UserProfileAdmin(admin.ModelAdmin):
    pass
admin.site.register(UserProfile, UserProfileAdmin)

class PositionAdmin(admin.ModelAdmin):
    pass
admin.site.register(Position, PositionAdmin)

class HoldingAdmin(admin.ModelAdmin):
    pass
admin.site.register(Holding, HoldingAdmin)

