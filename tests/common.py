import os
import tempfile
import copy
import pytest
from random import choice, randint
from atexit import register

from app.main import create_db, bundle_app
from app.middleware import db
from app.database import User, Operators, Office, Task, Serial, Waiting
from app.utils import absolute_path


NAMES = ('Aaron Enlightened', 'Abbott Father', 'Abel Breath', 'Abner Father',
         'Abraham Exalted', 'Adam Man', 'Addison Son', 'Adler Eagle',
         'Adley The Just', 'Adrian Dark', 'Aedan Fire', 'Alan Handsome',
         'Alastair Defender', 'Albern Noble', 'Albert Bright', 'Albion Fair',
         'Alden Guardian', 'Aldis Old', 'Aldrich Leader',
         'Alexander Protector', 'Alfred Wise', 'Avery Elfin Ruler',
         'Alvin Friend', 'Ambrose Immortal', 'Amery Industrious',
         'Amos A Burden', 'Andrew Valiant', 'Angus Unique', 'Ansel Nobel',
         'Anthony Priceless', 'Archer Bowman', 'Archibald Prince',
         'Arlen Pledge', 'Arnold Eagle', 'Arvel Wept', 'Atwater Waterside',
         'Atwood Forest', 'Aubrey Ruler', 'Austin Helpful',
         'Axel Peace', 'Baird Bard', 'Baldwin Friend', 'Barnaby Prophet',
         'Baron Nobleman', 'Barrett Bear-Like', 'Barry Marksman',
         'Bartholomew Warlike', 'Basil King-like')
PREFIXES = list(map(lambda i: chr(i).upper(), range(97,123)))

MODULES = [Waiting, Serial, User, Operators, Task, Office]
DB_PATH = absolute_path('testing.sqlite')


@pytest.fixture
def client():
    app = bundle_app({'LOGIN_DISABLED': True, 'WTF_CSRF_ENABLED': False})
    db_fd, app.config['DATABASE'] = tempfile.mkstemp()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'

    with app.test_client() as client:
        with app.app_context():
            create_db(app)
            teardown_tables(copy.copy(MODULES))
            fill_offices()
            fill_tasks()
            fill_users()
            fill_tickets()
        yield client

    register(lambda: os.path.isfile(DB_PATH) and os.remove(DB_PATH))
    os.close(db_fd)
    os.unlink(app.config['DATABASE'])


def teardown_tables(modules):
    if modules:
        for record in modules.pop().query.all():
            db.session.delete(record)
    
        db.session.commit()
        return teardown_tables(modules)


def fill_users(entry_number=10, role=None):
    for _ in range(entry_number):
        def recur():
            role_id = role or choice(range(1, 4))
            snm = "TEST" + str(randint(10000, 99999999))
            go = True if User.query.filter_by(name=snm).first() is None else False

            if not go:
                return recur()
            user = User(snm, snm, role_id)

            db.session.add(user)
            db.session.commit()
            role_id == 3 and db.session.add(Operators(
                id=user.id,
                office_id=choice(Office.query.all()).id
            ))

        recur()
    db.session.commit()


def fill_offices(entry_number=10):
    for _ in range(entry_number):
        prefix = choice([
            p for p in PREFIXES
            if not Office.query.filter_by(prefix=p).first()
        ] or [None]) or None

        prefix and db.session.add(Office(
            randint(10000, 9999999),
            prefix
        ))

    db.session.commit()


def fill_tasks(entry_number=10):
    for _ in range(entry_number):
        name = f'TEST{randint(10000, 99999999)}'
        offices = []
        # First task will be uncommon task
        number_of_offices = 1 if _ == 0 else choice(range(1, 5))

        while number_of_offices > len(offices):
            office = choice(Office.query.all())

            if office not in offices:
                offices.append(office)
        
        task = Task(name)
        db.session.add(task)
        db.session.commit()
        task.offices = offices
        db.session.commit()


def fill_tickets(entry_number=100):
    for _ in range(entry_number):
        last_ticket = Serial.query.order_by(Serial.number.desc()).first()
        number = (last_ticket.number if last_ticket else 100) + 1
        name = choice(NAMES)
        task = choice(Task.query.all())
        office = choice(task.offices)

        db.session.add(Serial(number=number, office_id=office.id,
                              task_id=task.id, name=name, n=True))
    db.session.commit()

    # Filling the waiting tickets stack
    tickets_to_fill = Serial.query.filter_by(p=False)\
                                  .order_by(Serial.number)\
                                  .limit(11 - Waiting.query.count())

    for ticket in tickets_to_fill:
        db.session.add(Waiting(number=ticket.number, office_id=ticket.office_id,
                               task_id=ticket.task_id, name=ticket.name, n=ticket.n))
    db.session.commit()