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
        cls.url_home = reverse('notes:home')
        cls.url_login = reverse('users:login')
        cls.url_logout = reverse('users:logout')
        cls.url_signup = reverse('users:signup')
        cls.url_list = reverse('notes:list')
        cls.url_detail = reverse('notes:detail', args=(cls.note.slug,))
        cls.url_edit = reverse('notes:edit', args=(cls.note.slug,))
        cls.url_delete = reverse('notes:delete', args=(cls.note.slug,))
        cls.url_success = reverse('notes:success')
        cls.url_add = reverse('notes:add')

    def test_redirect_for_anonymous_client_link(self):
        urls = (
            self.url_list,
            self.url_edit,
            self.url_delete,
            self.url_success,
            self.url_add,
        )
        for name in urls:
            with self.subTest(name=name):
                redirect_url = f'{self.url_login}?next={name}'
                response = self.client.get(name)
                self.assertRedirects(response, redirect_url)

    def test_access_client(self):
        access_links = (
            (self.url_home, self.client, HTTPStatus.OK),
            (self.url_login, self.client, HTTPStatus.OK),
            (self.url_logout, self.client, HTTPStatus.OK),
            (self.url_signup, self.client, HTTPStatus.OK),
            (self.url_list, self.author_client, HTTPStatus.OK),
            (self.url_success, self.author_client, HTTPStatus.OK),
            (self.url_add, self.author_client, HTTPStatus.OK),
            (self.url_detail, self.author_client, HTTPStatus.OK),
            (self.url_edit, self.author_client, HTTPStatus.OK),
            (self.url_delete, self.author_client, HTTPStatus.OK),
            (self.url_detail, self.reader_client, HTTPStatus.NOT_FOUND),
            (self.url_edit, self.reader_client, HTTPStatus.NOT_FOUND),
            (self.url_delete, self.reader_client, HTTPStatus.NOT_FOUND),
        )
        for name, client, status in access_links:
            with self.subTest(name=name, client=client, status=status):
                response = client.get(name)
                self.assertEqual(response.status_code, status)
