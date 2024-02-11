import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from blog.models import Post


"""Создание тестовых данных."""


@pytest.fixture
def user(django_user_model):
    return django_user_model.objects.create_user(
        username='TestUser',
        password='1234567'
    )


@pytest.fixture
def user_2(django_user_model):
    return django_user_model.objects.create_user(
        username='TestUser_2',
        password='1234567'
    )


@pytest.fixture
def token(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


@pytest.fixture
def user_client(token):
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token["access"]}')
    return client


@pytest.fixture
def token_admin(admin_user):
    refresh = RefreshToken.for_user(admin_user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


@pytest.fixture
def admin(token_admin):
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token_admin["access"]}')
    return client


@pytest.fixture
def post(user):
    return Post.objects.create(
        title='Пост',
        text='Тестовый пост 1',
        user=user
    )


@pytest.fixture
def post_2(user_2):
    return Post.objects.create(
        title='Чужой пост',
        text='Тестовый пост 2',
        user=user_2
    )


"""Тестирование API-endpoints, прав доступа."""


class TestPostAPI:

    @pytest.mark.django_db(transaction=True)
    def test_posts_not_found(self, client):
        response = client.get('/posts/')

        assert response.status_code != 404, (
            'Страница `/posts/` не найдена.'
        )

    @pytest.mark.django_db(transaction=True)
    def test_post_list_not_auth(self, client):
        response = client.get('/posts/')

        assert response.status_code == 200, (
            'Проверьте, что при GET запросе на `/posts/` '
            'без токена авторизации возвращается статус 200'
        )

        test_data = response.json()

        assert len(test_data) == Post.objects.count(), (
            'Проверьте, что при GET запросе на `/posts/` '
            'возвращается весь список постов'
        )

    @pytest.mark.django_db(transaction=True)
    def test_post_detail_not_auth(self, client, post):
        response = client.get(f'/posts/{post.id}/')

        assert response.status_code == 200, (
            'Проверьте, что при GET запросе на `/posts/{post.id}/` '
            'без токена авторизации возвращается статус 200'
        )

    @pytest.mark.django_db(transaction=True)
    def test_post_create(self, user_client, client, user):
        post_count = Post.objects.count()
        data = {}
        response = user_client.post('/posts/', data=data)

        assert response.status_code == 400, (
            'Проверьте, что при POST запросе на `/posts/` '
            'с неправильными данными возвращается статус 400'
        )

        data = {'title': 'Заголовок', 'text': 'Текст'}
        response = user_client.post('/posts/', data=data)

        assert response.status_code == 201, (
            'Проверьте, что при POST запросе на `/posts/` '
            'с правильными данными возвращается статус 201'
        )

        assert (
                response.json().get('user') is not None
                and response.json().get('user') == user.username
        ), (
            'Проверьте, что при POST запросе на `/posts/` '
            'автором указывается пользователь, от имени которого сделан запрос'
        )

        assert post_count + 1 == Post.objects.count(), (
            'Проверьте, что при POST запросе на `/posts/` создается пост'
        )

        response = client.post('/posts/', data=data)

        assert response.status_code == 401, (
            'Проверьте, что при POST запросе на `/posts/` '
            'неавторизованный пользователь не может создать запись'
        )

    @pytest.mark.django_db(transaction=True)
    def test_post_patch(self, client, user_client, admin, post, post_2):
        text = post.text
        new_text = 'Новый текст'
        data = {'text': new_text}
        response = user_client.patch(f'/posts/{post.id}/', data=data)

        assert response.status_code == 200, (
            'Проверьте, что при PATCH запросе на `posts/{id}/` '
            'от автора поста возвращается статус 200'
        )

        test_post = Post.objects.filter(id=post.id).first()

        assert test_post.text != text and test_post.text == new_text, (
            'Проверьте, что при PATCH запросе на `/posts/{id}/` '
            'пользователь изменяет пост'
        )

        text = post_2.text
        response = user_client.patch(f'/posts/{post_2.id}/', data=data)

        assert response.status_code == 403, (
            'Проверьте, что при PATCH запросе на `/posts/{id}/` '
            'для чужого поста возвращается статус 403'
        )

        test_post = Post.objects.filter(id=post_2.id).first()

        assert test_post.text == text and test_post.text != new_text, (
            'Проверьте, что при PATCH запросе на `/posts/{id}/` '
            'пользователь не изменяет чужой пост'
        )

        response = client.patch(f'/posts/{post_2.id}/', data=data)

        assert response.status_code == 401, (
            'Проверьте, что при PATCH запросе на `/posts/{id}/` '
            'неавторизованный пользователь не может изменить запись'
        )

        response = admin.patch(f'/posts/{post_2.id}/', data=data)

        assert response.status_code == 200, (
            'Проверьте, что при PATCH запросе на `posts/{id}/` '
            'от администратора возвращается статус 200'
        )

        test_post = Post.objects.filter(id=post_2.id).first()

        assert test_post.text != text and test_post.text == new_text, (
            'Проверьте, что при PATCH запросе на `/posts/{id}/` '
            'администратор изменяет чужой пост'
        )

    @pytest.mark.django_db(transaction=True)
    def test_post_delete(self, client, user_client, admin, post, post_2):
        response = client.delete(f'/posts/{post.id}/')
        test_post = Post.objects.filter(id=post.id).first()

        assert response.status_code == 401, (
            'Проверьте, что при DELETE запросе на `/posts/{id}/` '
            'неавторизованным пользователем возвращается статус 401'
        )

        assert test_post, (
            'Проверьте, что при DELETE запросе на `/posts/{id}/` '
            'неавторизованный пользователь не может удалить пост'
        )

        response = user_client.delete(f'/posts/{post_2.id}/')
        test_post = Post.objects.filter(id=post_2.id).first()

        assert response.status_code == 403, (
            'Проверьте, что при DELETE запросе на `/posts/{id}/` '
            'чужого поста возвращается статус 403'
        )

        assert test_post, (
            'Проверьте, что при DELETE запросе на `/posts/{id}/` '
            'пользователь не может удалить чужой пост'
        )

        response = user_client.delete(f'/posts/{post.id}/')
        test_post = Post.objects.filter(id=post.id).first()

        assert response.status_code == 204, (
            'Проверьте, что при DELETE запросе на `/posts/{id}/` '
            'автором поста возвращается статус 204'
        )

        assert not test_post, (
            'Проверьте, что при DELETE запросе на `/posts/{id}/` '
            'авторм пост удаляется'
        )

        response = admin.delete(f'/posts/{post_2.id}/')
        test_post = Post.objects.filter(id=post_2.id).first()

        assert response.status_code == 204, (
            'Проверьте, что при DELETE запросе на `/posts/{id}/` '
            'администратором возвращается статус 204'
        )

        assert not test_post, (
            'Проверьте, что при DELETE запросе на `/posts/{id}/` '
            'администратором пост удаляется'
        )
