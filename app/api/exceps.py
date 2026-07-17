from fastapi import Request
from fastapi.exceptions import ResponseValidationError, RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError as SQLAlchemyIntegrityError


class LoginError(Exception):
    pass

class ItemNotFoundError(Exception):
    pass

class NoPermissionError(Exception):
    pass

class ItemAlreadyExistsError(Exception):
    pass

class DatabaseIntegrityError(Exception):
    pass

class request_validation(Exception):
    pass

class response_validation(Exception):
    pass

class BadRequestError(Exception):
    pass

class UnauthorizedError(Exception):
    pass