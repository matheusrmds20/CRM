"""Testes HTTP de autenticacao: rate limit do login e invalidacao de token."""

from app.core.security import create_access_token
from app.models.users import UserDB

def test_rate_limit_login_por_username(client):
    """6 tentativas erradas para o mesmo username -> 429, mesmo na mesma origem."""
    form = {
        "username": "ratelimit-user",
        "password": "senha-errada",
    }
    for _ in range(5):
        resp = client.post("/api/v1/auth/login", data=form)
        assert resp.status_code == 401

    resp = client.post("/api/v1/auth/login", data=form)
    assert resp.status_code == 429

def test_rate_limit_nao_bloqueia_outro_username(client, existing_user):
    """Bloqueio de um username nao impede o login de outro usuario."""
    client.post("/api/v1/auth/login", data={"username": "outro-bloqueado", "password": "errada"})

    resp = client.post("/api/v1/auth/login", data={
        "username": existing_user.username,
        "password": "12345678",
    })
    assert resp.status_code == 200
    assert "access_token" in resp.json()

def test_token_invalidado_apos_troca_de_senha(client, auth_headers_owner, owner_user):
    """Token emitido antes da troca de senha passa a ser rejeitado (401)."""
    resp = client.get("/api/v1/users/me", headers=auth_headers_owner)
    assert resp.status_code == 200

    resp = client.patch(
        f"/api/v1/users/update_password/{owner_user.id}",
        headers=auth_headers_owner,
        json={"current_password": "12345678", "new_password": "nova-senha-forte"},
    )
    assert resp.status_code == 200

    resp = client.get("/api/v1/users/me", headers=auth_headers_owner)
    assert resp.status_code == 401

    resp = client.post("/api/v1/auth/login", data={
        "username": owner_user.username,
        "password": "nova-senha-forte",
    })
    assert resp.status_code == 200
    assert "access_token" in resp.json()