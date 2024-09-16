from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from .factories import BookFactory, UserFactory
from Books.models import Book

class BookAPITestCase(APITestCase):
    def setUp(self):
        self.user = UserFactory.create()
        self.token = RefreshToken.for_user(self.user).access_token
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        self.book_url = reverse('books-list')
        self.book_data = {
            'title': 'Test Book',
            'author': 'Test Author',
            'description': 'Test Description',
            'published_date': '2024-01-01',
            'price': '19.99',
        }

    def test_create_book(self):
        response = self.client.post(self.book_url, self.book_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        print(response.data, "++++++++++++++test_create_book+++++++++++++++++++")
        self.assertIn('title', response.data['data'])
        self.assertEqual(response.data['data']['title'], self.book_data['title'])

    def test_list_books(self):
        BookFactory.create(user=self.user) 
        response = self.client.get(self.book_url, format='json')
        print(response.data, "+++++++++++++++test_list_books++++++++++++++++++")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data['data']), 0)

    def test_retrieve_book(self):
        book = BookFactory.create(user=self.user)
        url = reverse('books-detail', kwargs={'pk': book.pk})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['title'], book.title)

    def test_update_book(self):
        book = BookFactory.create(user=self.user)
        url = reverse('books-detail', kwargs={'pk': book.pk})
        updated_data = {
            'title': 'Updated Title',
            'author': book.author,
            'description': book.description,
            'published_date': book.published_date,
            'price': book.price,
        }
        response = self.client.put(url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['title'], updated_data['title'])

    def test_partial_update_book(self):
        book = BookFactory.create(user=self.user)
        url = reverse('books-detail', kwargs={'pk': book.pk})
        updated_data = {'title': 'Partially Updated Title'}
        print(updated_data, "+++++++++++++++test__partial_update_book++++++++++++++++++")
        response = self.client.patch(url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['title'], updated_data['title'])

    def test_delete_book(self):
        book = BookFactory.create(user=self.user)
        url = reverse('books-detail', kwargs={'pk': book.pk})
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Book.objects.filter(pk=book.pk).exists())

    def test_create_book_unauthenticated(self):
        self.client.credentials()
        response = self.client.post(self.book_url, self.book_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_book_invalid_data(self):
        invalid_data = {
            'title': '',
            'author': '',
            'description': '',
            'published_date': '',
            'price': ''
        }
        response = self.client.post(self.book_url, invalid_data, format='json')
        print(response.data, "++++++++++++++test_create_book_invalid_data+++++++++++++++++++")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('errors', response.data)
        errors = response.data['errors']
        self.assertIn('title', errors)
        self.assertIn('author', errors)
        self.assertIn('description', errors)
        self.assertIn('published_date', errors)
        self.assertIn('price', errors)
        self.assertEqual(errors['title'][0].code, 'blank')
        self.assertEqual(errors['author'][0].code, 'blank')
        self.assertEqual(errors['description'][0].code, 'blank')
        self.assertEqual(errors['published_date'][0].code, 'invalid')
        self.assertEqual(errors['price'][0].code, 'invalid')

    def test_retrieve_book_invalid_id(self):
        url = reverse('books-detail', kwargs={'pk': 999})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_book_invalid_data(self):
        book = BookFactory.create(user=self.user)
        url = reverse('books-detail', kwargs={'pk': book.pk})
        invalid_data = {'title': ''}
        response = self.client.put(url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('title', response.data)

    def test_update_book_unauthorized(self):
        another_user = UserFactory.create()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {RefreshToken.for_user(another_user).access_token}')
        book = BookFactory.create(user=self.user)
        url = reverse('books-detail', kwargs={'pk': book.pk})
        updated_data = {'title': 'Unauthorized Update'}
        response = self.client.put(url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_book_unauthorized(self):
        another_user = UserFactory.create()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {RefreshToken.for_user(another_user).access_token}')
        book = BookFactory.create(user=self.user)
        url = reverse('books-detail', kwargs={'pk': book.pk})
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Book.objects.filter(pk=book.pk).exists())
