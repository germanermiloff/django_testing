from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from http import HTTPStatus

from notes.models import Note
from notes.forms import WARNING

from pytils.translit import slugify

User = get_user_model()

DATA = {
    'title': 'Новый заголовок',
    'text': 'Новый текст',
    'slug': 'new-slug'
}


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='author')
        cls.auth_user = User.objects.create(username='auth_user')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.author,
        )

    def test_user_can_create_note(self):
        self.client.force_login(self.author)
        url = reverse('notes:add')
        response = self.client.post(url, data=DATA)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 2)
        new_note = Note.objects.get(
            title=DATA['title'],
            text=DATA['text'],
            slug=DATA['slug']
        )
        self.assertEqual(new_note.title, DATA['title'])
        self.assertEqual(new_note.text, DATA['text'])
        self.assertEqual(new_note.slug, DATA['slug'])
        self.assertEqual(new_note.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        url = reverse('notes:add')
        response = self.client.post(url, DATA)
        login_url = reverse('users:login')
        expected_url = f'{login_url}?next={url}'
        self.assertRedirects(response, expected_url)
        self.assertEqual(Note.objects.count(), 1)

    def test_not_unique_slug(self):
        self.client.force_login(self.author)
        url = reverse('notes:add')
        response = self.client.post(url, data={
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': self.note.slug
        })
        self.assertFormError(response, 'form', 'slug',
                             errors=(self.note.slug + WARNING))
        assert Note.objects.count() == 1

    def test_empty_slug(self):
        self.client.force_login(self.author)
        url = reverse('notes:add')
        response = self.client.post(url, data={
            'title': 'Новый заголовок',
            'text': 'Новый текст',
        })
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 2)
        new_note = Note.objects.get(
            title='Новый заголовок',
            text='Новый текст',
        )
        expected_slug = slugify(DATA['title'])
        self.assertEqual(new_note.slug, expected_slug)

    def test_author_can_edit_note(self):
        self.client.force_login(self.author)
        url = reverse('notes:edit', args=(self.note.slug,))
        response = self.client.post(url, DATA)
        self.assertRedirects(response, reverse('notes:success'))
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, DATA['title'])
        self.assertEqual(self.note.text, DATA['text'])
        self.assertEqual(self.note.slug, DATA['slug'])

    def test_other_user_cant_edit_note(self):
        self.client.force_login(self.auth_user)
        url = reverse('notes:edit', args=(self.note.slug,))
        response = self.client.post(url, DATA)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_from_db = Note.objects.get(id=self.note.id)
        assert self.note.title == note_from_db.title
        assert self.note.text == note_from_db.text
        assert self.note.slug == note_from_db.slug
