import pytest
from http import HTTPStatus
from django.urls import reverse

pytestmark = pytest.mark.django_db

@pytest.mark.parametrize(
    'name',
    ('news:home', 'users:login', 'users:logout', 'users:signup')
)
def test_pages_availability_for_anonymous_user(client, name, news):
    '''
    Проверяем что главная страница доступна анонимному пользователю.
    Страницы регистрации пользователей,
    входа в учётную запись и выхода из неё доступны анонимным пользователям.
    '''
    url = reverse(name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


def test_detail_page(client, news):
    """Тест что страница отдельной новости доступна анонимному пользователю."""
    url = reverse('news:detail', args=(news.pk,))
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK),
        (pytest.lazy_fixture('not_author_client'), HTTPStatus.NOT_FOUND)
    )
)
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete')
)
def test_edit_delete_comment_for_users(
    name, comment, parametrized_client, expected_status
):
    """Тест что cтраницы удаления и редактирования комментария
    доступны автору комментария.
    """
    url = reverse(name, args=(comment.id,))
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete')
)
def test_redirect_for_anonymous(client, name, comment):
    """
    Проверяем, что при попытке перейти на страницу редактирования
    или удаления комментария анонимный пользователь перенаправляется
    на страницу авторизации.
    """
    login_url = reverse('users:login')
    url = reverse(name, args=(comment.id,))
    redirect_url = f'{login_url}?next={url}'
    response = client.get(url)
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == redirect_url
