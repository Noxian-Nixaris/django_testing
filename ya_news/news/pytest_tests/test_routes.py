from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects
from pytest_lazyfixture import lazy_fixture as lf


@pytest.mark.parametrize(
    'name', (lf('url_delete'), lf('url_edit'))
)
def test_access_for_anonymous_client(client, name, url_login):
    expected_url = f'{url_login}?next={name}'
    response = client.get(name)
    assertRedirects(response, expected_url)


@pytest.mark.parametrize(
    'reverse_url, parametrized_client, status', (
        (
            lf('url_comment_edit'),
            lf('author_client'),
            HTTPStatus.OK
        ),
        (
            lf('url_comment_edit'),
            lf('not_author_client'),
            HTTPStatus.NOT_FOUND
        ),
        (
            lf('url_comment_delete'),
            lf('author_client'),
            HTTPStatus.OK
        ),
        (
            lf('url_comment_delete'),
            lf('not_author_client'),
            HTTPStatus.NOT_FOUND
        ),
        (
            lf('url_home'),
            lf('client'),
            HTTPStatus.OK
        ),
        (
            lf('url_detail'),
            lf('client'),
            HTTPStatus.OK
        ),
        (
            lf('url_login'),
            lf('client'),
            HTTPStatus.OK
        ),
        (
            lf('url_logout'),
            lf('client'),
            HTTPStatus.OK
        ),
        (
            lf('url_signup'),
            lf('client'),
            HTTPStatus.OK
        )
    )
)
@pytest.mark.django_db
def test_redirect_for_client(reverse_url, parametrized_client, status):
    response = parametrized_client.get(reverse_url)
    assert response.status_code == status
