from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class ApplicationError(Exception):
    def __init__(self, message: str, status_code: int):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class ClientBaseError(ApplicationError):
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message, status_code)


class NotFoundError(ClientBaseError):
    def __init__(self, name: str, name_id: int):
        self.name = name
        self.name_id = name_id
        self.message = f"{name.capitalize()} with id {name_id} was not found."
        super().__init__(self.message, 404)


class UsernameAlreadyExistsException(ClientBaseError):
    def __init__(self, username: str):
        self.username = username
        self.message = f"Username '{username}' is already taken."
        super().__init__(self.message, 409)


class EmailAlreadyExistsException(ClientBaseError):
    def __init__(self, email: str):
        self.email = email
        self.message = f"Email '{email}' is already taken."
        super().__init__(self.message, 409)


class PasswordException(ClientBaseError):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message, 400)


class UnauthorizedException(ClientBaseError):
    def __init__(self, message: str = "Could not validate credentials."):
        self.message = message
        super().__init__(self.message, 401)


class AlreadySubscribedError(ClientBaseError):
    def __init__(self, author_id: int):
        self.message = f"Already subscribed to author with id {author_id}."
        super().__init__(self.message, 400)


class AlreadyUnsubscribedError(ClientBaseError):
    def __init__(self, author_id: int):
        self.message = f"Already unsubscribed from author with id {author_id}."
        super().__init__(self.message, 400)


async def exception_handler(request: Request, exc: ClientBaseError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


def register_exception_handlers(app: FastAPI):
    app.add_exception_handler(ClientBaseError, exception_handler)
