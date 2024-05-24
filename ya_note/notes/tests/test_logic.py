from http import HTTPStatus
from pytils.translit import slugify

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note
from notes.forms import WARNING

User = get_user_model()


class TestLogic(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Комментатор')
        cls.new_post = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': 'new-slug'
        }

    def test_user_can_create_note(self):
        self.client.force_login(self.author)
        url = reverse('notes:add')
        response = self.client.post(url, data=self.new_post)
        self.assertRedirects(response, reverse('notes:success'))
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        new_note = Note.objects.get()
        self.assertEqual(new_note.title, self.new_post['title'])
        self.assertEqual(new_note.text, self.new_post['text'])
        self.assertEqual(new_note.slug, self.new_post['slug'])
        self.assertEqual(new_note.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        url = reverse('notes:add')
        response = self.client.post(url, data=self.new_post)
        login_url = reverse('users:login')
        expected_url = f'{login_url}?next={url}'
        self.assertRedirects(response, expected_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_empty_slug(self):
        self.client.force_login(self.author)
        url = reverse('notes:add')
        self.new_post.pop('slug')
        response = self.client.post(url, data=self.new_post)
        self.assertRedirects(response, reverse('notes:success'))
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        new_note = Note.objects.get()
        expected_slug = slugify(self.new_post['title'])
        self.assertEqual(new_note.slug, expected_slug)


class TestLogicdb(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Комментатор')
        cls.reader = User.objects.create(username='Посторонний')
        cls.new_post = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': 'new-slug'
        }
        cls.note = Note.objects.create(
            title='title',
            text='text',
            slug='slug',
            author=cls.author
        )

    def test_other_user_cant_delete_note(self):

        url = reverse('notes:delete', args=(self.note.slug,))
        self.client.force_login(self.reader)
        response = self.client.post(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_author_can_delete_note(self):
        url = reverse('notes:delete', args=(self.note.slug,))
        self.client.force_login(self.author)
        response = self.client.post(url)
        self.assertRedirects(response, reverse('notes:success'))
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_other_user_cant_edit_note(self):
        url = reverse('notes:edit', args=(self.note.slug,))
        self.client.force_login(self.reader)
        response = self.client.post(url, data=self.new_post)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_from_db = Note.objects.get(id=self.note.id)
        self.assertEqual(self.note.title, note_from_db.title)
        self.assertEqual(self.note.text, note_from_db.text)
        self.assertEqual(self.note.slug, note_from_db.slug)

    def test_author_can_edit_note(self):
        url = reverse('notes:edit', args=(self.note.slug,))
        self.client.force_login(self.author)
        response = self.client.post(url, data=self.new_post)
        self.assertRedirects(response, reverse('notes:success'))
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.new_post['title'])
        self.assertEqual(self.note.text, self.new_post['text'])
        self.assertEqual(self.note.slug, self.new_post['slug'])

    def test_not_unique_slug(self):
        self.client.force_login(self.author)
        url = reverse('notes:add')
        self.new_post['slug'] = self.note.slug
        response = self.client.post(url, data=self.new_post)
        self.assertFormError(
            response, 'form', 'slug', errors=(self.note.slug + WARNING))
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
