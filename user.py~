from flask_login import UserMixin


class UserNotFoundError(Exception):
    pass


class User(UserMixin):
    # TODO: you know what to do...
    USERS = {
        # username: password
        'roger': 'troll0',
        'mary': 'jane',
        '1': '1'
    }

    id = None
    password = None

    def __init__(self, id):
        if id not in self.USERS:
            raise UserNotFoundError()
        self.id = id
        self.password = self.USERS[id]

    @classmethod
    def get(self_class, id):
        try:
            return self_class(id)
        except UserNotFoundError:
            return None
