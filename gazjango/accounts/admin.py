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

class HoldingInline(admin.TabularInline):
    model = Holding

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user__username', 'user__first_name', 'user__last_name', 'user__is_staff', 'position')
    inlines = [ HoldingInline ]
admin.site.register(UserProfile, UserProfileAdmin)

class PositionAdmin(admin.ModelAdmin):
    pass
admin.site.register(Position, PositionAdmin)
