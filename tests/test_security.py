from http import HTTPStatus

from jwt import decode

from fastzero.security import create_access_token, settings


def test_jwt():
    data = {'test': 'test'}
    token = create_access_token(data)

    decoded = decode(token, settings.SECRET_KEY, algorithms=['HS256'])

    assert decoded['test'] == data['test']
    assert decoded['exp']


def test_jwt_invalid_token(client):
    resp = client.delete(
        '/users/1',
        headers={'Authorization': 'Bearer token-errado'},
    )

    assert resp.status_code == HTTPStatus.UNAUTHORIZED
    assert resp.json() == {'detail': 'could not validate credentials'}
