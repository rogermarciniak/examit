from flask_login import UserMixin


class UserNotFoundError(Exception):
    pass


class User(UserMixin):
    # TODO: needs to be dehardcoded if time allows for a proper user solution
    USERS = {
        # username: password
        'roger': 'troll0',
        'mary': 'jane'
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
