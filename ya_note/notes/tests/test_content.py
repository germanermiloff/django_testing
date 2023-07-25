from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


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

    def test_notes_list_for_different_users(self):
        users_statuses = (
            (self.author, True),
            (self.auth_user, False),
        )
        for user, note_in_list in users_statuses:
            self.client.force_login(user)
            url = reverse('notes:list')
            response = self.client.get(url)
            object_list = response.context['object_list']
            assert (self.note in object_list) is note_in_list

    def test_pages_contains_form(self):
        self.client.force_login(self.author)
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,)),
        )
        for name, args in urls:
            url = reverse(name, args=args)
            response = self.client.get(url)
            assert 'form' in response.context
