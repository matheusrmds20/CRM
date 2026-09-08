import asyncio
import time
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Request
from app.api.router import router
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from app.api.exceps import ItemNotFoundError, NoPermissionError, ItemAlreadyExistsError, DatabaseIntegrityError, LoginError, BadRequestError
from sqlalchemy.exc import IntegrityError
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from starlette.middleware.base import BaseHTTPMiddleware
from alembic import command
from alembic.config import Config


BASE_DIR = Path(__file__).resolve().parent.parent
ALEMBIC_INI = BASE_DIR / "alembic.ini"






app = FastAPI()


origins = [
    "http://localhost",
    "http://127.0.0.1",
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "http://localhost:5173",
    "http://localhost:5173/leads",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    
)

limiter = Limiter(key_func=get_remote_address)

app.state.limiter = limiter

app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

class SecurityMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        # response.headers["Content-Security-Policy"] = "default-src 'self'"
        
        return response

app.add_middleware(SecurityMiddleware)

app.include_router(router, prefix="/api/v1")    


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.exception_handler(ItemNotFoundError)
def item_not_found_handler(request: Request, exc: ItemNotFoundError):
    return JSONResponse(
        status_code=404,
        content={"detail": str(exc)},
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
        content={"detail": str(exc)},
    )

@app.exception_handler(IntegrityError)
def sql_integrity_error_handler(request: Request, exc: IntegrityError):
    return JSONResponse(
        status_code=400,
        content={"detail": "Empresa informada nao existe ou conflito de integridade"},
    )

