"""
Management command to create demo user for testing.
Run with: python manage.py create_demo_user
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Creates a demo user for testing the application'

    def handle(self, *args, **options):
        email = 'demo@example.com'
        username = 'demouser'
        password = 'demo1234'

        # Check if user already exists
        if User.objects.filter(email=email).exists():
            self.stdout.write(self.style.WARNING(f'User with email {email} already exists.'))
            return

        # Create the demo user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name='Demo',
            last_name='User'
        )

        self.stdout.write(self.style.SUCCESS(f'Successfully created demo user:'))
        self.stdout.write(f'  Email: {email}')
        self.stdout.write(f'  Password: {password}')
