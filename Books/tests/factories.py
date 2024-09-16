import factory
from django.contrib.auth.models import User
from Books.models import Book

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'user{n}')
    password = factory.PostGenerationMethodCall('set_password', 'password')

class BookFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Book

    user = factory.SubFactory(UserFactory)
    title = 'Test Book'
    author = 'Test Author'
    description = 'Test Description'
    published_date = '2024-01-01'
    price = '19.99'
