from datetime import datetime, timedelta
from django.utils import timezone

import pytest
from django.conf import settings
from django.test.client import Client

from news.forms import BAD_WORDS
from news.models import Comment, News


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news(author):
    news = News.objects.create(
        title='Заголовок',
        text='Текст заметки'
    )
    return news


@pytest.fixture
def comment(author, news):
    comment = Comment.objects.create(
        text='Комментарий',
        news=news,
        author=author
    )
    return comment


@pytest.fixture
def news_pk(news):
    return (news.pk,)


@pytest.fixture
def comment_pk(comment):
    return (comment.pk,)


@pytest.fixture
def comment_data():
    return {'text': 'Комментарий'}


@pytest.fixture
def bulk_news(author):
    today = datetime.today()
    all_news = [
        News(
            title=f'Новость {index}',
            text='Текст.',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    return News.objects.bulk_create(all_news)


@pytest.fixture
def all_comments(author, news):
    now = timezone.now()
    for index in range(10):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Текст{index}'
        )
        comment.created = now + timedelta(days=index)
    print(comment)
    return comment


@pytest.fixture
def bad_words_data():
    return {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
