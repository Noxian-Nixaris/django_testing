from datetime import datetime, timedelta

import pytest
from django.conf import settings
from django.test.client import Client
from django.urls import reverse
from django.utils import timezone

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
    News.objects.bulk_create(all_news)


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
        comment.save()


@pytest.fixture
def url_home():
    return reverse('news:home')


@pytest.fixture
def url_detail(news):
    return reverse('news:detail', args=(news.pk,))


@pytest.fixture
def url_delete(news):
    return reverse('news:delete', args=(news.pk,))


@pytest.fixture
def url_edit(news):
    return reverse('news:edit', args=(news.pk,))


@pytest.fixture
def url_comment_edit(comment):
    return reverse('news:edit', args=(comment.pk,))


@pytest.fixture
def url_comment_delete(comment):
    return reverse('news:delete', args=(comment.pk,))
