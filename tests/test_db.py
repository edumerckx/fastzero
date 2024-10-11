from dataclasses import asdict

from sqlalchemy import select

from fastzero.models import Todo, TodoState, User


def test_create_user(session, mock_db_time):
    with mock_db_time(model=User) as time:
        new_user = User(username='test', password='pass', email='test@test.com')
        session.add(new_user)
        session.commit()

    user = session.scalar(select(User).where(User.username == 'test'))

    expected = {
        'id': 1,
        'username': 'test',
        'password': 'pass',
        'email': 'test@test.com',
        'todos': [],
        'created_at': time,
        'updated_at': time,
    }

    assert asdict(user) == expected


def test_create_todo(session, user):
    todo = Todo(
        title='test todo',
        description='test',
        state=TodoState.draft,
        user_id=user.id,
    )

    session.add(todo)
    session.commit()
    session.refresh(todo)

    local_user = session.scalar(select(User).where(User.id == user.id))

    assert todo in local_user.todos
