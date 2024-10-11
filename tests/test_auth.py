from http import HTTPStatus

from freezegun import freeze_time


def test_get_token(client, user):
    resp = client.post(
        '/auth/token',
        data={'username': user.username, 'password': user.clean_password},
    )
    token = resp.json()

    assert resp.status_code == HTTPStatus.OK
    assert 'access_token' in token
    assert 'token_type' in token


def test_token_expired(client, user):
    with freeze_time('2024-01-01 12:00:00'):
        resp = client.post(
            '/auth/token',
            data={'username': user.username, 'password': user.clean_password},
        )

        assert resp.status_code == HTTPStatus.OK
        token = resp.json()['access_token']

    with freeze_time('2024-01-01 12:31:00'):
        resp = client.put(
            f'/users/{user.id}',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'username': 'test',
                'email': 'email@test.com',
                'password': 'pass',
            },
        )

        assert resp.status_code == HTTPStatus.UNAUTHORIZED
        assert resp.json() == {'detail': 'could not validate credentials'}


def test_token_inexistent_user(client):
    resp = client.post(
        '/auth/token',
        data={'username': 'test', 'password': 'pass'},
    )

    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert resp.json() == {'detail': 'incorrect username or password'}


def test_token_wrong_password(client, user):
    resp = client.post(
        '/auth/token',
        data={'username': user.username, 'password': 'xxxxxx'},
    )

    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert resp.json() == {'detail': 'incorrect username or password'}


def test_refresh_token(client, user, token):
    resp = client.post(
        '/auth/refresh_token',
        headers={'Authorization': f'Bearer {token}'},
    )

    data = resp.json()

    assert resp.status_code == HTTPStatus.OK
    assert 'access_token' in data
    assert 'token_type' in data
    assert data['token_type'] == 'bearer'


def test_token_expired_dont_refresh(client, user):
    with freeze_time('2024-01-01 12:00:00'):
        resp = client.post(
            '/auth/token',
            data={'username': user.username, 'password': user.clean_password},
        )

        assert resp.status_code == HTTPStatus.OK
        token = resp.json()['access_token']

    with freeze_time('2024-01-01 12:31:00'):
        resp = client.post(
            '/auth/refresh_token',
            headers={'Authorization': f'Bearer {token}'},
        )

        assert resp.status_code == HTTPStatus.UNAUTHORIZED
        assert resp.json() == {'detail': 'could not validate credentials'}
