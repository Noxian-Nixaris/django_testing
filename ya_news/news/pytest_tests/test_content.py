import pytest

from news.forms import CommentForm
from yanews import settings

pytestmark = pytest.mark.django_db


def test_news_count(client, bulk_news, url_home):
    response = client.get(url_home)
    news_list = response.context['object_list']
    counter = news_list.count()
    assert counter == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_order(client, bulk_news, url_home):
    response = client.get(url_home)
    news_list = response.context['object_list']
    all_dates = [news.date for news in news_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


def test_comments_order(client, news, url_detail, all_comments):
    response = client.get(url_detail)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


def test_anonymous_client_has_no_form(client, url_detail):
    response = client.get(url_detail)
    assert 'form' not in response.context


def test_authorized_client_has_form(author_client, url_detail):
    response = author_client.get(url_detail)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
