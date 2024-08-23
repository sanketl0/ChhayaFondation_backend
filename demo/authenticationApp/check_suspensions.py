# management/commands/check_suspensions.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from .models import CustomUser

class Command(BaseCommand):
    help = 'Check and lift user suspensions'

    def handle(self, *args, **options):
        now = timezone.now()
        users_to_restore = CustomUser.objects.filter(is_suspended=True, suspension_end_date__lte=now)
        for user in users_to_restore:
            user.is_suspended = False
            user.suspension_end_date = None
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Restored user: {user.username}'))
