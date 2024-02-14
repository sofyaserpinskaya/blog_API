import pytest

from blog.models import Post


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
