from http import HTTPStatus

from django.urls import reverse

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

from pytest_django.asserts import assertRedirects, assertFormError

import pytest


NEW_TEXT = 'Новый текст'


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, news):
    url = reverse('news:detail', args=(news.id,))
    client.post(url, data={'text': NEW_TEXT})
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_user_can_create_comment(admin_client, news):
    url = reverse('news:detail', args=(news.id,))
    admin_client.post(url, data={'text': NEW_TEXT})
    comments_count = Comment.objects.count()
    assert comments_count == 1
    comment = Comment.objects.get()
    assert comment.text == comment.text
    assert comment.news == news
    assert comment.author != admin_client


def test_user_cant_use_bad_words(admin_client, news):
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    url = reverse('news:detail', args=(news.id,))
    response = admin_client.post(url, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_author_can_delete_comment(author_client, news, comment):
    news_url = reverse('news:detail', args=(news.id,))
    url_to_comments = reverse('news:delete', args=(comment.id,))
    response = author_client.delete(url_to_comments)
    assertRedirects(response, news_url + '#comments')
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_user_cant_delete_comment_of_another_user(admin_client, comment):
    comment_url = reverse('news:delete', args=(comment.id,))
    response = admin_client.delete(comment_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count = Comment.objects.count()
    assert comments_count == 1


def test_author_can_edit_comment(author_client, news, comment):
    news_url = reverse('news:detail', args=(news.id,))
    comment_url = reverse('news:edit', args=(comment.id,))
    response = author_client.post(comment_url, data={'text': NEW_TEXT})
    assertRedirects(response, news_url + '#comments')
    comment.refresh_from_db()
    assert comment.text == NEW_TEXT


def test_user_cant_edit_comment_of_another_user(admin_client, comment):
    comment_url = reverse('news:edit', args=(comment.id,))
    response = admin_client.post(comment_url, data={'text': NEW_TEXT})
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text != NEW_TEXT
