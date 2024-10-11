from http import HTTPStatus

from fastzero.schemas import UserPublic


def test_create_user(client):
    data = {'username': 'test', 'email': 'test@test.com', 'password': 'test'}

    expected = {'username': 'test', 'email': 'test@test.com', 'id': 1}

    resp = client.post(
        '/users/',
        json=data,
    )

    assert resp.status_code == HTTPStatus.CREATED
    assert resp.json() == expected


def test_create_user_username_exists(client, user):
    data = {
        'username': user.username,
        'email': 'test@test.com',
        'password': 'pass',
    }
    expected = {'detail': 'username already exists'}

    resp = client.post(
        '/users/',
        json=data,
    )

    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert resp.json() == expected


def test_create_user_email_exists(client, user):
    data = {'username': 'test', 'email': user.email, 'password': 'pass'}
    expected = {'detail': 'email already exists'}

    resp = client.post(
        '/users/',
        json=data,
    )

    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert resp.json() == expected


def test_read_users(client):
    expected = {'users': []}
    resp = client.get('/users/')
    assert resp.status_code == HTTPStatus.OK
    assert resp.json() == expected


def test_read_users_with_users(client, user):
    user_schema = UserPublic.model_validate(user).model_dump()
    expected = {'users': [user_schema]}
    resp = client.get('/users/')
    assert resp.status_code == HTTPStatus.OK
    assert resp.json() == expected


def test_read_user(client, user):
    user_schema = UserPublic.model_validate(user).model_dump()
    resp = client.get('/users/1')
    assert resp.status_code == HTTPStatus.OK
    assert resp.json() == user_schema


def test_read_user_not_found(client):
    resp = client.get('/users/12345')
    expected = {'detail': 'user not found'}
    assert resp.status_code == HTTPStatus.NOT_FOUND
    assert resp.json() == expected


def test_update_user(client, user, token):
    data = {
        'username': 'update_test',
        'email': 'update_test@test.com',
        'password': 'test',
    }
    expected = {
        'username': 'update_test',
        'email': 'update_test@test.com',
        'id': 1,
    }
    resp = client.put(
        f'/users/{user.id}',
        json=data,
        headers={'Authorization': f'Bearer {token}'},
    )
    assert resp.status_code == HTTPStatus.OK
    assert resp.json() == expected


def test_update_user_integrity_error(client, user, other_user, token):
    data = {
        'username': other_user.username,
        'email': 'update_test@test.com',
        'password': 'test',
    }

    resp = client.put(
        f'/users/{user.id}',
        json=data,
        headers={'Authorization': f'Bearer {token}'},
    )

    expected = {'detail': 'username or email already exists'}

    assert resp.status_code == HTTPStatus.CONFLICT
    assert resp.json() == expected


def test_update_user_with_wrong_user(client, other_user, token):
    resp = client.put(
        f'/users/{other_user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={'username': 'bob', 'email': 'bob@test.com', 'password': 'test'},
    )

    assert resp.status_code == HTTPStatus.FORBIDDEN
    assert resp.json() == {'detail': 'not enough permissions'}


def test_delete_user(client, user, token):
    resp = client.delete(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
    )
    expected = {'message': 'user deleted'}
    assert resp.status_code == HTTPStatus.OK
    assert resp.json() == expected


def test_delete_user_with_wrong_user(client, other_user, token):
    resp = client.delete(
        f'/users/{other_user.id}',
        headers={'Authorization': f'Bearer {token}'},
    )
    expected = {'detail': 'not enough permissions'}
    assert resp.status_code == HTTPStatus.FORBIDDEN
    assert resp.json() == expected
