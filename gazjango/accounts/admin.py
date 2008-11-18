from django.contrib import admin
from gazjango.accounts.models import UserKind, ContactMethod, ContactItem
from gazjango.accounts.models import UserProfile, Position, Holding

class UserKindAdmin(admin.ModelAdmin):
    pass
admin.site.register(UserKind, UserKindAdmin)

class ContactMethodAdmin(admin.ModelAdmin):
    pass
admin.site.register(ContactMethod, ContactMethodAdmin)


class HoldingInline(admin.TabularInline):
    model = Holding

class ContactItemInline(admin.TabularInline):
    model = ContactItem

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('username', 'name', 'is_staff', 'position')
    search_fields = ['^user__username', '^user__first_name', '^user__last_name', '^user__email']
    inlines = [ HoldingInline, ContactItemInline ]
admin.site.register(UserProfile, UserProfileAdmin)


class PositionAdmin(admin.ModelAdmin):
    pass
admin.site.register(Position, PositionAdmin)
