from fastapi import FastAPI
from app.api.router import router
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from app.api.exceps import ItemNotFoundError, NoPermissionError, ItemAlreadyExistsError, DatabaseIntegrityError, request_validation, response_validation, LoginError, BadRequestError, UnauthorizedError


app = FastAPI()


app.include_router(router, prefix="/api/v1")    


@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.exception_handler(Exception)
def exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Erro ao executar a acao"},
    )

@app.exception_handler(ItemNotFoundError)
def item_not_found_handler(request: Request, exc: ItemNotFoundError):
    return JSONResponse(
        status_code=404,
        content={"detail": "Item nao encontrado"},
    )

@app.exception_handler(NoPermissionError)
def no_permission_handler(request: Request, exc: NoPermissionError):
    return JSONResponse(
        status_code=403,
        content={"detail": "Voce nao tem permissao para executar essa acao"},
    )

@app.exception_handler(ItemAlreadyExistsError)
def item_already_exists_handler(request: Request, exc: ItemAlreadyExistsError):
    return JSONResponse(
        status_code=409,
        content={"detail": "Item ja existente"},
    )

@app.exception_handler(DatabaseIntegrityError)
def database_integrity_handler(request: Request, exc: DatabaseIntegrityError):
    return JSONResponse(
        status_code=400,
        content={"detail": "Nao foi possivel criar ou atualizar o item por conflito de integridade"},
    )

@app.exception_handler(request_validation)
def request_validation_error_handler(request: Request, exc: request_validation):
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )

@app.exception_handler(response_validation)
def response_validation_error_handler(request: Request, exc: response_validation):
    return JSONResponse(
        status_code=500,
        content={"detail": "Erro ao validar a resposta da API"},
    )

@app.exception_handler(LoginError)
def login_error_handler(request: Request, exc: LoginError):
    return JSONResponse(
        status_code=401,
        content={"detail": "Usuário ou senha incorreto"},
    )

@app.exception_handler(BadRequestError)
def bad_request_error_handler(request: Request, exc: BadRequestError):
    return JSONResponse(
        status_code=400,
        content={"detail": "Nenhum campo foi preenchido"},
    )

def unauthorized_error_handler(request: Request, exc: UnauthorizedError):
    return JSONResponse(
        status_code=401,
        content={"detail": "Voce nao tem permissao para executar essa acao"},
    )   