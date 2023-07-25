from django.urls import reverse

import pytest


@pytest.mark.django_db
def test_news_count(client, list_news):
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    news_count = len(object_list)
    assert news_count == len(list_news)


@pytest.mark.django_db
def test_news_order(client, list_news):
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    all_news = [news for news in object_list]
    sorted_news = sorted(all_news, key=lambda x: x.date, reverse=True)
    assert sorted_news == list_news


@pytest.mark.django_db
def test_comments_order(client, news, list_comments):
    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)
    news = response.context['news']
    all_comments = news.comment_set.all()
    assert [all_comments[0], all_comments[1]] == list_comments


@pytest.mark.django_db
def test_anonymous_client_has_no_form(client, comment):
    url = reverse('news:detail', args=(comment.id,))
    response = client.get(url)
    assert 'form' not in response.context


def test_authorized_client_has_form(author_client, comment):
    url = reverse('news:detail', args=(comment.id,))
    response = author_client.get(url)
    assert 'form' in response.context
