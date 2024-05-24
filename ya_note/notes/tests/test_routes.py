from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.reader = User.objects.create(username='Читатель простой')
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
        self.client.force_login(self.author)
        for link in urls:
            with self.subTest(link=link):
                url = reverse(link)
                responce = self.client.get(url)
                self.assertEqual(responce.status_code, HTTPStatus.OK)

    def test_access_author_client(self):
        urls = ('notes:detail', 'notes:edit', 'notes:delete')
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in urls:
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.note.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)
