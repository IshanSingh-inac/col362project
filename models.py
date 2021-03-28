class User:
    def __init__(self, id, username, gender ,password):
        self.id = id
        self.username = username
        self.password = password
        self.gender = gender

    def __repr__(self):
        return f'<User: {self.username}>'