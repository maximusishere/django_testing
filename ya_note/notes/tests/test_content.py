from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()

class TestContent(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create_user(username='author')
        cls.not_author = User.objects.create_user(username='not_author')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст заметки',
            author=cls.author
        )

    def test_note_for_author(self):
        self.client.force_login(self.author)
        url = reverse('notes:list')
        response = self.client.get(url)
        object_list = response.context['object_list']
        self.assertIn(self.note, object_list)

    def test_note_not_author(self):
        self.client.force_login(self.not_author)
        url = reverse('notes:list')
        response = self.client.get(url)
        object_list = response.context['object_list']
        self.assertNotIn(self.note, object_list)

    def test_create_note_page_contains_form(self):
        self.client.force_login(self.author)
        url = reverse('notes:add')
        response = self.client.get(url)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)

    def test_edit_note_page_contains_form(self):
        self.client.force_login(self.author)
        url = reverse('notes:edit', args=[self.note.slug])
        response = self.client.get(url)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)
