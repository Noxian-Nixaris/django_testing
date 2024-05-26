from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.reader = User.objects.create(username='Читатель простой')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.note = Note.objects.create(
            title='title',
            text='text',
            slug='slug',
            author=cls.author
        )

    def test_access_page(self):
        urls = (
            ('notes:home', None),
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_for_anonymous_client_link(self):
        login_url = reverse('users:login')
        args = (self.note.slug,)
        urls = (
            ('notes:list', None),
            ('notes:edit', args),
            ('notes:delete', args),
            ('notes:success', None),
            ('notes:add', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_access_auth_client(self):
        urls = ('notes:list', 'notes:success', 'notes:add')
        for link in urls:
            with self.subTest(link=link):
                url = reverse(link)
                responce = self.author_client.get(url)
                self.assertEqual(responce.status_code, HTTPStatus.OK)

    def test_access_client(self):
        access_links = (
            ('notes:detail', self.author_client, HTTPStatus.OK),
            ('notes:edit', self.author_client, HTTPStatus.OK),
            ('notes:delete', self.author_client, HTTPStatus.OK),
            ('notes:detail', self.reader_client, HTTPStatus.NOT_FOUND),
            ('notes:edit', self.reader_client, HTTPStatus.NOT_FOUND),
            ('notes:delete', self.reader_client, HTTPStatus.NOT_FOUND),
        )
        for name, client, status in access_links:
            with self.subTest(name=name, client=client, status=status):
                url = reverse(name, args=(self.note.slug,))
                response = client.get(url)
                self.assertEqual(response.status_code, status)
