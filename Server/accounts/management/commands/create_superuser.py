from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import UserType


class Command(BaseCommand):
    help = 'Create a super admin user'

    def handle(self, *args, **options):
        User = get_user_model()
        
        username = 'admin'
        email = 'admin@wewin.com'
        password = 'admin123'
        
        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(f'User {username} already exists'))
            return
        
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
            user_type=UserType.SUPER_ADMIN
        )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created super admin user!\n'
                f'Username: {username}\n'
                f'Email: {email}\n'
                f'Password: {password}\n'
                f'Please change the password after first login!'
            )
        )
