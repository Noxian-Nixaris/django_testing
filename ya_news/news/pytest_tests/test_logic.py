from http import HTTPStatus

from pytest_django.asserts import assertFormError, assertRedirects

from ..models import Comment

from ..forms import BAD_WORDS, WARNING

bad_words_list = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}


def test_anonymous_user_cant_create_comment(client, comment_data, url_detail):
    pre_count = Comment.objects.count()
    client.post(url_detail, comment_data)
    comments_count = Comment.objects.count()
    assert comments_count == pre_count


def test_user_can_create_comment(
    author_client, author, comment_data, news, url_detail
):
    data_base = Comment.objects.all()
    data_base.delete
    author_client.post(url_detail, comment_data)
    comments_count = Comment.objects.count()

    comment = Comment.objects.get()
    assert comments_count == 1
    assert comment.text == comment_data['text']
    assert comment.news == news
    assert comment.author == author


def test_user_cant_use_bad_words(author_client, url_detail):
    pre_count = Comment.objects.count()
    response = author_client.post(url_detail, data=bad_words_list)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    comments_count = Comment.objects.count()
    assert comments_count == pre_count


def test_author_can_delete_comment(
    author_client, url_delete, url_detail, comment
):
    pre_count = Comment.objects.count()
    url_to_comments = url_detail + '#comments'
    response = author_client.delete(url_delete)
    assertRedirects(response, url_to_comments)
    comments_count = Comment.objects.count()
    assert comments_count == pre_count - 1


def test_user_cant_delete_comment_of_another_user(
    not_author_client, url_comment_delete
):
    pre_count = Comment.objects.count()
    response = not_author_client.delete(url_comment_delete)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count = Comment.objects.count()
    assert comments_count == pre_count


def test_author_can_edit_comment(
    author_client, author, url_comment_edit, url_detail, comment
):
    new_comment = {'text': 'Обновлённый комментарий'}
    url_to_comments = url_detail + '#comments'
    response = author_client.post(url_comment_edit, data=new_comment)
    assertRedirects(response, url_to_comments)
    comment.refresh_from_db()
    assert comment.text == new_comment['text']
    assert comment.author == author


def test_user_cant_edit_comment_of_another_user(
    not_author_client, comment, url_comment_edit
):
    new_comment = {'text': 'Обновлённый комментарий'}
    response = not_author_client.post(url_comment_edit, data=new_comment)
    assert response.status_code == HTTPStatus.NOT_FOUND
    old_comment = Comment.objects.get(pk=comment.pk)
    assert comment.text == old_comment.text
