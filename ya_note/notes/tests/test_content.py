from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestContentPage(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Комментатор')
        cls.reader = User.objects.create(username='Посторонний')
        cls.my_note = Note.objects.create(
            title='title',
            text='text',
            slug='slug',
            author=cls.author
        )

    def test_note_in_list_for_author(self):
        url = reverse('notes:list')
        self.client.force_login(self.author)
        response = self.client.get(url)
        object_list = response.context['object_list']
        self.assertIn(self.my_note, object_list)

    def test_note_not_in_list_for_another_user(self):
        url = reverse('notes:list')
        self.client.force_login(self.reader)
        response = self.client.get(url)
        object_list = response.context['object_list']
        self.assertNotIn(self.my_note, object_list)

    def test_pages_contains_form(self):
        pages = (
            ('notes:add', None),
            ('notes:edit', (self.my_note.slug,)),
        )
        self.client.force_login(self.author)
        for link, args in pages:
            with self.subTest(link=link, args=args):
                url = reverse(link, args=args)
                response = self.client.get(url)
                self.assertIsInstance(response.context['form'], NoteForm)
