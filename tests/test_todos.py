from http import HTTPStatus

import factory.fuzzy
from freezegun import freeze_time

from fastzero.models import Todo, TodoState


class TodoFactory(factory.Factory):
    class Meta:
        model = Todo

    title = factory.Faker('text')
    description = factory.Faker('text')
    state = factory.fuzzy.FuzzyChoice(TodoState)
    user_id = 1


def test_create_todo(client, token):
    with freeze_time('2024-01-01 12:00:00'):
        resp = client.post(
            '/todos/',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'title': 'test todo',
                'description': 'test',
                'state': 'draft',
            },
        )

        expected_keys = (
            'id',
            'title',
            'description',
            'state',
            'created_at',
            'updated_at',
        )
        data = resp.json()

        assert resp.status_code == HTTPStatus.CREATED
        for key in expected_keys:
            assert key in data
        assert data['title'] == 'test todo'
        assert data['description'] == 'test'
        assert data['state'] == TodoState.draft


def test_list_todos_should_return_5_todos(session, client, user, token):
    session.bulk_save_objects(TodoFactory.create_batch(5, user_id=user.id))
    session.commit()

    resp = client.get(
        '/todos/',
        headers={'Authorization': f'Bearer {token}'},
    )
    expected = 5

    assert resp.status_code == HTTPStatus.OK
    assert len(resp.json()['todos']) == expected


def test_list_todos_pagination_should_return_2_todos(
    session, client, user, token
):
    session.bulk_save_objects(TodoFactory.create_batch(5, user_id=user.id))
    session.commit()

    resp = client.get(
        '/todos/?offset=1&limit=2',
        headers={'Authorization': f'Bearer {token}'},
    )
    expected = 2

    assert resp.status_code == HTTPStatus.OK
    assert len(resp.json()['todos']) == expected


def test_list_todos_filter_title(session, client, user, token):
    session.bulk_save_objects(
        TodoFactory.create_batch(5, user_id=user.id, title='Test todo')
    )
    session.bulk_save_objects(
        TodoFactory.create_batch(2, user_id=user.id, title='Special todo')
    )
    session.commit()

    resp = client.get(
        '/todos/?title=Special',
        headers={'Authorization': f'Bearer {token}'},
    )
    expected = 2

    assert resp.status_code == HTTPStatus.OK
    assert len(resp.json()['todos']) == expected


def test_list_todos_filter_description(session, client, user, token):
    session.bulk_save_objects(
        TodoFactory.create_batch(5, user_id=user.id, description='description')
    )
    session.bulk_save_objects(
        TodoFactory.create_batch(2, user_id=user.id, description='lorem ipsum')
    )
    session.commit()

    resp = client.get(
        '/todos/?description=ipsum',
        headers={'Authorization': f'Bearer {token}'},
    )
    expected = 2

    assert resp.status_code == HTTPStatus.OK
    assert len(resp.json()['todos']) == expected


def test_list_todos_filter_state(session, client, user, token):
    session.bulk_save_objects(
        TodoFactory.create_batch(5, user_id=user.id, state=TodoState.doing)
    )
    session.bulk_save_objects(
        TodoFactory.create_batch(2, user_id=user.id, state=TodoState.done)
    )
    session.commit()

    resp = client.get(
        '/todos/?state=doing',
        headers={'Authorization': f'Bearer {token}'},
    )
    expected = 5

    assert resp.status_code == HTTPStatus.OK
    assert len(resp.json()['todos']) == expected


def test_patch_todo(session, client, user, token):
    todo = TodoFactory(user_id=user.id)

    session.add(todo)
    session.commit()

    resp = client.patch(
        f'/todos/{todo.id}',
        json={'title': 'test update'},
        headers={'Authorization': f'Bearer {token}'},
    )

    assert resp.status_code == HTTPStatus.OK
    assert resp.json()['title'] == 'test update'


def test_patch_todo_not_found(client, token):
    resp = client.patch(
        '/todos/10',
        json={'title': 'title update'},
        headers={'Authorization': f'Bearer {token}'},
    )

    expected = {'detail': 'task not found'}

    assert resp.status_code == HTTPStatus.NOT_FOUND
    assert resp.json() == expected


def test_delete_todo(session, client, user, token):
    todo = TodoFactory(user_id=user.id)

    session.add(todo)
    session.commit()

    resp = client.delete(
        f'/todos/{todo.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    expected = {'message': 'task deleted'}

    assert resp.status_code == HTTPStatus.OK
    assert resp.json() == expected


def test_delete_todo_not_found(client, token):
    resp = client.delete(
        '/todos/10',
        headers={'Authorization': f'Bearer {token}'},
    )

    expected = {'detail': 'task not found'}

    assert resp.status_code == HTTPStatus.NOT_FOUND
    assert resp.json() == expected


def test_get_todo(session, client, user, token):
    todo = TodoFactory(
        user_id=user.id, title='test', description='test', state=TodoState.done
    )
    session.add(todo)
    session.commit()

    resp = client.get(
        f'/todos/{todo.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    data = resp.json()

    assert resp.status_code == HTTPStatus.OK
    assert data['title'] == 'test'
    assert data['description'] == 'test'
    assert data['state'] == TodoState.done


def test_get_todo_not_found(client, token):
    resp = client.get(
        '/todos/111',
        headers={'Authorization': f'Bearer {token}'},
    )

    expected = {'detail': 'task not found'}

    assert resp.status_code == HTTPStatus.NOT_FOUND
    assert resp.json() == expected
