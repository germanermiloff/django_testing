import pytest

from news.models import News, Comment

from datetime import datetime


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client


@pytest.fixture
def news():
    now = datetime.today
    news = News.objects.create(
        title='Заголовок',
        text='Текст новости',
        date=now,
    )
    return news


@pytest.fixture
def comment(news, author):
    comment = Comment.objects.create(
        text='Текст комментария',
        created=datetime.today,
        news=news,
        author=author,
    )
    return comment
