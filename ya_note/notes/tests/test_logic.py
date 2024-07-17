from django.contrib.auth import get_user_model
from pytils.translit import slugify
from django.test import TestCase
from django.urls import reverse
from notes.forms import WARNING
from http import HTTPStatus

from notes.models import Note

User = get_user_model()


class TestCreateNote(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.user = User.objects.create(username='Пользователь Простой')
        cls.form_data = {
            'title': 'Заголовок',
            'text': 'Текст заметки или записки.',
        }

    def test_user_can_create_note(self):
        self.client.force_login(self.author)
        url = reverse('notes:add')
        response = self.client.post(url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get()
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        url = reverse('notes:add')
        response = self.client.post(url, data=self.form_data)
        login_url = reverse('users:login')
        expected_url = f'{login_url}?next={url}'
        self.assertRedirects(response, expected_url)
        assert Note.objects.count() == 0

    def test_not_unique_slug(self):
        note = Note.objects.create(author=self.author, **self.form_data)
        url = reverse('notes:add')
        self.client.force_login(self.author)
        self.form_data['slug'] = note.slug
        response = self.client.post(url, data=self.form_data)
        self.assertFormError(
            response, 'form', 'slug', errors=(note.slug + WARNING)
        )
        assert Note.objects.count() == 1
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(
            self.form_data['slug'],
            expected_slug,
            msg=(
                f'Ожидался slug: {expected_slug},'
                f' но был: {self.form_data["slug"]}'
            )
        )
        """Вот здесь я вывожу ошибку понятным
           языком может и в остальном коде так сделаю :)"""

    def test_author_can_edit_note(self):
        note = Note.objects.create(author=self.author, **self.form_data)
        self.client.force_login(self.author)
        url = reverse('notes:edit', args=(note.slug,))
        self.form_data['slug'] = note.slug
        response = self.client.post(url, self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        note.refresh_from_db()
        assert note.title == self.form_data['title']
        assert note.text == self.form_data['text']
        assert note.slug == self.form_data['slug']

    def test_other_user_cant_edit_note(self):
        note = Note.objects.create(author=self.author, **self.form_data)
        self.client.force_login(self.user)
        url = reverse('notes:edit', args=(note.slug,))
        response = self.client.post(url, self.form_data)
        assert response.status_code == HTTPStatus.NOT_FOUND
        note_from_db = Note.objects.get(slug=note.slug)
        assert note.title == note_from_db.title
        assert note.text == note_from_db.text
        assert note.slug == note_from_db.slug

    def test_author_can_delete_note(self):
        note = Note.objects.create(author=self.author, **self.form_data)
        self.client.force_login(self.author)
        url = reverse('notes:delete', args=(note.slug,))
        response = self.client.post(url)
        self.assertRedirects(response, reverse('notes:success'))
        assert Note.objects.count() == 0

    def test_other_user_cant_delete_note(self):
        note = Note.objects.create(author=self.author, **self.form_data)
        self.client.force_login(self.user)
        url = reverse('notes:delete', args=(note.slug,))
        response = self.client.post(url)
        assert response.status_code == HTTPStatus.NOT_FOUND
        assert Note.objects.count() == 1
