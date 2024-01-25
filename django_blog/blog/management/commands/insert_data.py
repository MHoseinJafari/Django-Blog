from django.core.management.base import BaseCommand
from blog.models import Blog,Category
from accounts.models import User,Profile
from faker import Faker

from datetime import datetime
import random

category_list = [
    'fun',
    'currency',
    'politics'
]

class Command(BaseCommand):
    help = "create a test blog"

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.faker = Faker()

    def handle(self, *args, **options):
        user = User.objects.create_user(email = self.faker.email(), password = 'm@1234567')
        Profile.objects.create(user=user)
       
        for name in category_list:
            Category.objects.get_or_create(name=name)

        for _ in range(3):
            Blog.objects.create(
                author = user,
                title = self.faker.paragraph(nb_sentences=1),
                content = self.faker.paragraph(nb_sentences=10),
                category = Category.objects.get(name=random.choice(category_list)),
                created_date = datetime.now(),

            )
