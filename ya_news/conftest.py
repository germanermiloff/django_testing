from django.conf import settings
from django.utils import timezone

from news.models import News, Comment

from datetime import datetime, timedelta

import pytest


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client


@pytest.fixture
def news():
    news = News.objects.create(
        title='Заголовок',
        text='Текст новости',
        date=datetime.today(),
    )
    return news


@pytest.fixture
def comment(news, author):
    comment = Comment.objects.create(
        text='Текст комментария',
        created=datetime.today(),
        news=news,
        author=author,
    )
    return comment


@pytest.fixture
def list_news():
    today = datetime.today()
    list_news = [
        News.objects.create(
            title='Новость {index}',
            text='Текст новости',
            date=today - timedelta(days=index)
        ) for index in range(settings.NEWS_COUNT_ON_HOME_PAGE)]
    return list_news


@pytest.fixture
def list_comments(news, author):
    now = timezone.now()
    list_comment = [
        Comment.objects.create(
            text='Текст {index}',
            created=now + timedelta(days=index),
            news=news,
            author=author,
        ) for index in range(2)]
    return list_comment
