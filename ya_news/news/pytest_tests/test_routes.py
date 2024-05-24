from http import HTTPStatus

from django.urls import reverse
import pytest
from pytest_django.asserts import assertRedirects


@pytest.mark.parametrize(
    'name, news_object',
    (
        ('news:home', None),
        ('news:detail', pytest.lazy_fixture('news')),
        ('users:login', None),
        ('users:logout', None),
        ('users:signup', None)
    )
)
@pytest.mark.django_db
def test_pages_availability(client, name, news_object):
    if news_object is not None:
        url = reverse(name, args=(news_object.pk,))
    else:
        url = reverse(name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'user, access', (
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK),
        (pytest.lazy_fixture('not_author_client'), HTTPStatus.NOT_FOUND)
    )
)
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete')
)
def test_availability_for_comment_edit_and_delete(user, access, name, comment):
    url = reverse(name, args=(comment.pk,))
    response = user.get(url)
    assert response.status_code == access


@pytest.mark.parametrize(
    'name, args', (
        ('news:edit', pytest.lazy_fixture('comment_pk')),
        ('news:delete', pytest.lazy_fixture('comment_pk')),
    )
)
def test_redirect_for_anonymous_client(client, name, args):
    login_url = reverse('users:login')
    url = reverse(name, args=args)
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)


@pytest.mark.parametrize(
    'name, args', (
        ('news:edit', pytest.lazy_fixture('comment_pk')),
        ('news:delete', pytest.lazy_fixture('comment_pk')),
    )
)
def test_redirect_for_author_client(not_author_client, name, args):
    url = reverse(name, args=args)
    response = not_author_client.get(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
