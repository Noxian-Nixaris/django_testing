from http import HTTPStatus

from django.urls import reverse
from pytest_django.asserts import assertFormError, assertRedirects

from ..models import Comment

from ..forms import WARNING


def test_anonymous_user_cant_create_comment(client, comment_data, news_pk):
    url = reverse('news:detail', args=news_pk)
    form_data = comment_data
    client.post(url, form_data)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_user_can_create_comment(
    author_client, author, comment_data, news, news_pk
):
    url = reverse('news:detail', args=news_pk)
    form_data = comment_data
    author_client.post(url, form_data)
    comments_count = Comment.objects.count()
    comment = Comment.objects.get()
    assert comments_count == 1
    assert comment.text == comment_data['text']
    assert comment.news == news
    assert comment.author == author


def test_user_cant_use_bad_words(author_client, bad_words_data, news_pk):
    url = reverse('news:detail', args=news_pk)
    response = author_client.post(url, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_author_can_delete_comment(author_client, news_pk, comment):
    url = reverse('news:delete', args=news_pk)
    news_url = reverse('news:detail', args=news_pk)
    url_to_comments = news_url + '#comments'
    response = author_client.delete(url)
    assertRedirects(response, url_to_comments)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_user_cant_delete_comment_of_another_user(not_author_client, news_pk):
    url = reverse('news:delete', args=news_pk)
    response = not_author_client.delete(url)
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_author_can_edit_comment(author_client, news_pk, comment, comment_pk):
    new_comment = {'text': 'Обновлённый комментарий'}
    url = reverse('news:edit', args=comment_pk)
    news_url = reverse('news:detail', args=news_pk)
    url_to_comments = news_url + '#comments'
    response = author_client.post(url, data=new_comment)
    assertRedirects(response, url_to_comments)
    comment.refresh_from_db()
    assert comment.text == new_comment['text']


def test_user_cant_edit_comment_of_another_user(
    not_author_client, comment, comment_pk
):
    new_comment = {'text': 'Обновлённый комментарий'}
    url = reverse('news:edit', args=comment_pk)
    response = not_author_client.post(url, data=new_comment)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text != new_comment['text']
