from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestContentPage(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Комментатор')
        cls.reader = User.objects.create(username='Посторонний')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.my_note = Note.objects.create(
            title='title',
            text='text',
            slug='slug',
            author=cls.author
        )
        cls.url_list = reverse('notes:list')

    def test_note_in_list_for_author(self):
        response = self.author_client.get(self.url_list)
        note_list = response.context['object_list']
        self.assertIn(self.my_note, note_list)

    def test_note_not_in_list_for_another_user(self):
        response = self.reader_client.get(self.url_list)
        note_list = response.context['object_list']
        self.assertNotIn(self.my_note, note_list)

    def test_pages_contains_form(self):
        pages = (
            ('notes:add', None),
            ('notes:edit', (self.my_note.slug,)),
        )
        for link, args in pages:
            with self.subTest(link=link, args=args):
                url = reverse(link, args=args)
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
