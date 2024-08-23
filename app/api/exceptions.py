class NotFoundError(Exception):
    def __init__(self, name: str, name_id: int):
        self.name = name
        self.name_id = name_id
        self.message = f"{name.capitalize()} with id {name_id} was not found."
        super().__init__(self.message)


class UsernameAlreadyExistsException(Exception):
    def __init__(self, username: str):
        self.username = username
        self.message = f"Username '{username}' is already taken."
        super().__init__(self.message)


class EmailAlreadyExistsException(Exception):
    def __init__(self, email: str):
        self.email = email
        self.message = f"Email '{email}' is already taken."
        super().__init__(self.message)


class PasswordException(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)
