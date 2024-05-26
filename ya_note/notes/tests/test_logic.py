from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


class TestLogic(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Комментатор')
        cls.reader = User.objects.create(username='Посторонний')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.new_post = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': 'new-slug'
        }
        cls.url_add = reverse('notes:add')
        cls.url_success = reverse('notes:success')
        cls.url_login = reverse('users:login')
        cls.note = Note.objects.create(
            title='title',
            text='text',
            slug='slug',
            author=cls.author
        )
        cls.url_delete = reverse('notes:delete', args=(cls.note.slug,))
        cls.url_edit = reverse('notes:edit', args=(cls.note.slug,))

    def test_user_can_create_note(self):
        data_base = Note.objects.all()
        data_base.delete()
        response = self.author_client.post(self.url_add, data=self.new_post)
        self.assertRedirects(response, self.url_success)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        new_note = Note.objects.get()
        self.assertEqual(new_note.title, self.new_post['title'])
        self.assertEqual(new_note.text, self.new_post['text'])
        self.assertEqual(new_note.slug, self.new_post['slug'])
        self.assertEqual(new_note.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        pre_count = Note.objects.count()
        response = self.client.post(self.url_add, data=self.new_post)
        expected_url = f'{self.url_login}?next={self.url_add}'
        self.assertRedirects(response, expected_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, pre_count)

    def test_empty_slug(self):
        self.new_post.pop('slug')
        data_base = Note.objects.all()
        data_base.delete()
        response = self.author_client.post(self.url_add, data=self.new_post)
        self.assertRedirects(response, self.url_success)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        new_note = Note.objects.get()
        expected_slug = slugify(self.new_post['title'])
        self.assertEqual(new_note.slug, expected_slug)

    def test_other_user_cant_delete_note(self):
        pre_count = Note.objects.count()
        response = self.reader_client.post(self.url_delete)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, pre_count)

    def test_author_can_delete_note(self):
        pre_count = Note.objects.count()
        response = self.author_client.delete(self.url_delete)
        self.assertRedirects(response, self.url_success)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, pre_count - 1)

    def test_other_user_cant_edit_note(self):
        response = self.reader_client.post(self.url_edit, data=self.new_post)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_from_db = Note.objects.get(id=self.note.id)
        self.assertEqual(self.note.title, note_from_db.title)
        self.assertEqual(self.note.text, note_from_db.text)
        self.assertEqual(self.note.slug, note_from_db.slug)
        self.assertEqual(self.note.author, self.author)

    def test_author_can_edit_note(self):
        response = self.author_client.post(self.url_edit, data=self.new_post)
        self.assertRedirects(response, self.url_success)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.new_post['title'])
        self.assertEqual(self.note.text, self.new_post['text'])
        self.assertEqual(self.note.slug, self.new_post['slug'])
        self.assertEqual(self.note.author, self.author)

    def test_not_unique_slug(self):
        pre_count = Note.objects.count()
        self.new_post['slug'] = self.note.slug
        response = self.author_client.post(self.url_add, data=self.new_post)
        self.assertFormError(
            response, 'form', 'slug', errors=(self.note.slug + WARNING))
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, pre_count)
