import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.models import User
from .models import Post, Like, Connection


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def create_user(db):
    def make_user(username, password="testpass123"):
        user = User.objects.create_user(username=username, password=password)
        return user
    return make_user


@pytest.fixture
def get_token(client, create_user):
    def generate(username):
        user = create_user(username)
        response = client.post(reverse('login'), {
            'username': username,
            'password': 'testpass123'
        })
        token = response.data['token']
        return user, token
    return generate


@pytest.mark.django_db
def test_user_registration(client):
    response = client.post(reverse('register'), {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'testpass123'
    })
    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_user_login(get_token):
    _, token = get_token('loginuser')
    assert token is not None


@pytest.mark.django_db
def test_post_creation(client, get_token):
    user, token = get_token('poster')
    client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
    response = client.post(reverse('create-post'), {
        'content': 'My first post'
    })
    assert response.status_code == status.HTTP_201_CREATED
    assert Post.objects.filter(author=user).exists()


@pytest.mark.django_db
def test_post_list(client, get_token):
    user, token = get_token('poster')
    client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
    client.post(reverse('create-post'), {'content': 'New post'})
    response = client.get(reverse('list-posts'))
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) > 0


@pytest.mark.django_db
def test_like_unlike_post(client, get_token):
    user, token = get_token('liker')
    client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
    post = Post.objects.create(content='Like this', author=user)

    # Like
    like_url = reverse('like-post', args=[post.id])
    res_like = client.post(like_url)
    assert res_like.status_code == status.HTTP_200_OK
    assert Like.objects.filter(user=user, post=post).exists()

    # Unlike
    unlike_url = reverse('unlike-post', args=[post.id])
    res_unlike = client.post(unlike_url)
    assert res_unlike.status_code == status.HTTP_200_OK
    assert not Like.objects.filter(user=user, post=post).exists()


@pytest.mark.django_db
def test_send_connection(client, get_token, create_user):
    user1, token1 = get_token('user1')
    user2 = create_user('user2')
    client.credentials(HTTP_AUTHORIZATION=f'Token {token1}')
    response = client.post(reverse('send-connection', args=[user2.id]))
    assert response.status_code == status.HTTP_200_OK
    assert Connection.objects.filter(from_user=user1, to_user=user2).exists()


@pytest.mark.django_db
def test_incoming_requests(client, get_token, create_user):
    user1, token1 = get_token('u1')
    user2, token2 = get_token('u2')
    client.credentials(HTTP_AUTHORIZATION=f'Token {token1}')
    client.post(reverse('send-connection', args=[user2.id]))

    client.credentials(HTTP_AUTHORIZATION=f'Token {token2}')
    response = client.get(reverse('incoming-requests'))
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) > 0


@pytest.mark.django_db
def test_recommendations(client, get_token):
    user, token = get_token('reco_user')
    client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
    response = client.get(reverse('user-recommendations'))
    assert response.status_code == status.HTTP_200_OK
