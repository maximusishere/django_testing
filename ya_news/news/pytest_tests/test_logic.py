from django.urls import reverse
from pytest_django.asserts import assertFormError, assertRedirects
from news.models import Comment
from news.forms import BAD_WORDS, WARNING

COMMENT_TEXT = 'Просто коммент'
NEW_COMMENT_TEXT = 'Обновлённый комментарий'


def test_anonymous_user_cant_create_comment(client, news):
    """Проверим, что анонимный пользователь не может отправить комментарий."""
    client.post(
        'news:edit', kwargs=('pk', news.id), data={'заголовок': 'Сам коммент'}
    )
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_user_can_create_comment(comment):
    """Проверим, что авторизованный пользователь может отправить комментарий"""
    comments_count = Comment.objects.count()
    assert comments_count == 1
    created_comment = Comment.objects.get()
    assert created_comment.text == 'Просто коммент'
    assert created_comment.news == comment.news
    assert created_comment.author == comment.author


def test_user_cant_use_bad_words(author_client, news):
    """
    Проверим, что если комментарий содержит запрещённые слова,
    он не будет опубликован
    """
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    url = reverse('news:detail', args=(news.id,))
    response = author_client.post(url, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_author_can_delete_comment(comment, author_client):
    """Авторизованный пользователь может удалять свои комментарии."""
    comments_count = Comment.objects.count()
    assert comments_count == 1
    delete_url = reverse('news:delete', args=[comment.id])
    author_client.delete(delete_url)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_user_cant_delete_comment_of_another_user(comment, client):
    """Простой юзер не может удалять чужие комментарии."""
    comments_count = Comment.objects.count()
    assert comments_count == 1
    delete_url = reverse('news:delete', args=[comment.id])
    client.delete(delete_url)
    comments_count = Comment.objects.count()
    assert comments_count == 1


def test_author_can_edit_comment(comment, author_client):
    """Авторизованный пользователь может редактировать свои комментарии."""
    edit_url = reverse('news:edit', args=[comment.id])
    form_data = {'text': NEW_COMMENT_TEXT}
    response = author_client.post(edit_url, form_data)
    news_url = reverse('news:detail', args=(comment.pk,))
    url_to_comments = news_url + '#comments'
    assertRedirects(response, url_to_comments)
    comment.refresh_from_db()
    assert comment.text == NEW_COMMENT_TEXT


def test_user_cant_edit_comment_of_another_user(comment, client):
    """Простой юзер не может редактировать чужие комментарии."""
    edit_url = reverse('news:edit', args=[comment.id])
    form_data = {'text': NEW_COMMENT_TEXT}
    client.post(edit_url, form_data)
    comment.refresh_from_db()
    assert comment.text == COMMENT_TEXT
