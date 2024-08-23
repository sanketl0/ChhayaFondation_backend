from django.contrib import admin
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from .models import CustomUser, PendingUser
from django.utils import timezone
from datetime import timedelta
import logging


logger = logging.getLogger(__name__)
User = get_user_model()

@admin.register(CustomUser)

class CustomUser(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_active', 'is_suspended')
    actions = ['suspend_users', 'restore_users','activate_users', 'deactivate_users']

    def suspend_users(self, request, queryset):
        for user in queryset:
            if not user.is_suspended:
                user.is_suspended = True
                user.suspension_end_date = timezone.now() + timedelta(days=1)
                user.save()
                self.send_suspension_email(user, request)
                self.message_user(request, f"User '{user.username}' has been suspended.")
            else:
                self.message_user(request, f"User '{user.username}' is already suspended.")

    def restore_users(self, request, queryset):
        for user in queryset:
            if user.is_suspended:
                user.is_suspended = False
                user.suspension_end_date = None
                user.save()
                self.send_restoration_email(user, request)
                self.message_user(request, f"User '{user.username}' has been restored.")
            else:
                self.message_user(request, f"User '{user.username}' is not suspended.")

    def activate_users(self, request, queryset):
        for user in queryset:
            if not user.is_active:
                user.is_active = True
                user.save()
                self.send_activation_email(user, request)
                self.message_user(request, f"User '{user.username}' has been activated.")
            else:
                self.message_user(request, f"User '{user.username}' is already active.")

    def deactivate_users(self, request, queryset):
        for user in queryset:
            if user.is_active:
                user.is_active = False
                user.save()
                self.send_deactivation_email(user, request)
                self.message_user(request, f"User '{user.username}' has been deactivated.")
            else:
                self.message_user(request, f"User '{user.username}' is already inactive.")

    def send_suspension_email(self, user, request):
        try:
            subject = 'Your Account Has Been Suspended'
            message = (
                f'Your account has been suspended due to unexpected behavior.\n\n'
                f'You will not be able to log in until {user.suspension_end_date}.'
            )
            recipient_list = [user.email]
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)
        except Exception as e:
            logger.error(f"Error sending suspension email to {user.email}: {e}", exc_info=True)
            self.message_user(request, f"Failed to send suspension email to {user.username}.")

    def send_restoration_email(self, user, request):
        try:
            subject = 'Your Account Has Been Restored'
            message = (
                f'Your account has been restored. You can now log in and use the services as usual.'
            )
            recipient_list = [user.email]
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)
        except Exception as e:
            logger.error(f"Error sending restoration email to {user.email}: {e}", exc_info=True)
            self.message_user(request, f"Failed to send restoration email to {user.username}.")

    def send_deactivation_email(self, user, request):
        try:
            subject = 'Your Account Has Been Deactivated'
            message = (
                f'Your account has been deactivated. If you believe this is a mistake, please contact support.'
            )
            recipient_list = [user.email]
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)
            logger.info(f"Deactivation email sent to {user.email}.")
        except Exception as e:
            logger.error(f"Error sending deactivation email to {user.email}: {e}", exc_info=True)
            self.message_user(request, f"Failed to send deactivation email to {user.username}.")

    def send_activation_email(self, user, request):
        try:
            subject = 'Your Account Has Been Activated'
            message = (
                f'Your account has been activated. You can now log in and use the services as usual.'
            )
            recipient_list = [user.email]
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)
            logger.info(f"Activation email sent to {user.email}.")
        except Exception as e:
            logger.error(f"Error sending activation email to {user.email}: {e}", exc_info=True)
            self.message_user(request, f"Failed to send activation email to {user.username}.")


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
                    password=pending_user.password ,
                    first_name = pending_user.first_name,
                    last_name = pending_user.last_name,
                    mobile_number = pending_user.mobile_number
                )
                pending_user.is_approved = True
                pending_user.save()
                self.approve_user_mail(user)
                self.message_user(request, f"User '{pending_user.username}' approved and created.")
            else:
                self.message_user(request, f"User '{pending_user.username}' is already approved.")

    def delete_users(self, request, queryset):
        for pending_user in queryset:
            if not pending_user.is_approved:
                pending_user.delete()
                self.send_deletion_email(pending_user)
                self.message_user(request, f"Pending user '{pending_user.username}' has been deleted.")
            else:
                self.message_user(request, f"User '{pending_user.username}' is already approved and cannot be deleted.")

    delete_users.short_description = 'Delete selected pending_users'

    def approve_user_mail(self,user):
        try:

            user.is_active = True
            user.save()

            # Send email to user
            subject = 'Your Account Has Been Approved'
            message = f'Your account has been approved. You can now log in with the following credentials:\n\n' \
                      f'Email: {user.email}\n' \
                      f'Password: Use the password you set during signup.'

            recipient_list = [user.email]
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)

        except Exception as e:
            logger.error(f"Error during user approval: {e}", exc_info=True)
            raise

    def send_deletion_email(self, pending_user):
        try:
            subject = 'Registration Request Denied'
            message = f'We are sorry, but your registration request has been denied. You are not able to register on this site.'
            recipient_list = [pending_user.email]
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)
        except Exception as e:
            logger.error(f"Error during sending deletion email: {e}", exc_info=True)
            raise






