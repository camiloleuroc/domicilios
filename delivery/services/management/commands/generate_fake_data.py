from django.core.management.base import BaseCommand
from services.models import User, Location
from faker import Faker

class Command(BaseCommand):
    help = 'Generates 20 drivers with false addresses'

    def handle(self, *args, **kwargs):
        fake = Faker()

        # Create 20 drivers
        for _ in range(20):
            # Create driver user
            user = User.objects.create(
                username=fake.user_name(),
                password=fake.password(),
                plate=fake.license_plate(),
                is_driver=True
            )
            
            # Create a dummy address for each driver
            Location.objects.create(
                user=user,
                address=fake.address(),
                latitude=fake.latitude(),
                longitude=fake.longitude()
            )

        self.stdout.write(self.style.SUCCESS('¡20 drivers with false addresses generated!'))