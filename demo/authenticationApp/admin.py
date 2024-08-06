from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import CustomUser, PendingUser
# from django.contrib.auth.models import User

# Register your models here.
User = get_user_model()

admin.site.register(CustomUser)

@admin.register(PendingUser)
class PendingUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_approved', 'created_at')
    actions = ['approve_users','delete_users']

    def approve_users(self, request, queryset):
        for pending_user in queryset:
            if not pending_user.is_approved:
                user = User.objects.create_user(
                    username=pending_user.username,
                    email=pending_user.email,
                    password=pending_user.password
                )
                pending_user.is_approved = True
                pending_user.save()
                self.message_user(request, f"User '{pending_user.username}' approved and created.")
            else:
                self.message_user(request, f"User '{pending_user.username}' is already approved.")

    def delete_users(self, request, queryset):
        for pending_user in queryset:
            if not pending_user.is_approved:
                pending_user.delete()
                self.message_user(request, f"Pending user '{pending_user.username}' has been deleted.")
            else:
                self.message_user(request, f"User '{pending_user.username}' is already approved and cannot be deleted.")

    delete_users.short_description = 'Delete selected pending users'


