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

class BadRequestError(Exception):
    pass
