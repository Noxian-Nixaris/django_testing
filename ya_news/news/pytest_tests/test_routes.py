from http import HTTPStatus

import pytest
from django.urls import reverse
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
    'reverse_url, parametrized_client, status', (
        (
            pytest.lazy_fixture('url_comment_edit'),
            pytest.lazy_fixture('author_client'),
            HTTPStatus.OK
        ),
        (
            pytest.lazy_fixture('url_comment_edit'),
            pytest.lazy_fixture('not_author_client'),
            HTTPStatus.NOT_FOUND
        ),
        (
            pytest.lazy_fixture('url_comment_delete'),
            pytest.lazy_fixture('author_client'),
            HTTPStatus.OK
        ),
        (
            pytest.lazy_fixture('url_comment_delete'),
            pytest.lazy_fixture('not_author_client'),
            HTTPStatus.NOT_FOUND
        ),
    )
)
def test_redirect_for_client(reverse_url, parametrized_client, status):
    response = parametrized_client.get(reverse_url)
    assert response.status_code == status
