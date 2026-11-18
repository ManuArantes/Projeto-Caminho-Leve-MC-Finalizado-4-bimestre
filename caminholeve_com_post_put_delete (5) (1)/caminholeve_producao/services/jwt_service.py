# =====================================================================
#  jwt_service.py  —  SERVIÇO DE AUTENTICAÇÃO VIA JWT (JSON Web Token)
# =====================================================================
#  O que é JWT?
#    É um token assinado digitalmente (padrão RFC 7519) dividido em 3 partes
#    separadas por ponto (Header.Payload.Signature):
#      1) Header: algoritmo de assinatura (HS256) e tipo (JWT).
#      2) Payload (claims): dados do usuário logado (e-mail, nome, tipo) +
#         data de criação (iat) e data de expiração (exp).
#      3) Signature: assinatura criptográfica gerada com a chave secreta do
#         servidor. Se alguém tentar alterar o payload no navegador (ex.: mudar
#         tipo para 'ADM'), a assinatura fica inválida e o token é rejeitado!
#
#  Como funciona neste sistema:
#    - No LOGIN, geramos o token JWT e o salvamos em um cookie HttpOnly
#      chamado `jwt_token` (protegido contra leitura via XSS no JavaScript)
#      e também aceitamos o cabeçalho `Authorization: Bearer <token>`.
#    - A cada requisição (@app.before_request), o servidor valida a assinatura
#      e a validade (exp) do JWT antes de liberar o acesso às rotas protegidas.

import os
from datetime import datetime, timedelta, timezone
from functools import wraps
import jwt
from flask import request, redirect, flash, jsonify, g

# Chave secreta usada para assinar e verificar os tokens JWT (mínimo 32 bytes recomendado para HS256 / RFC 7518)
JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "caminholeve_jwt_secret_key_producao_2026_hs256")
JWT_ALGORITHM = "HS256"
JWT_EXP_HOURS = 8  # Tempo de duração do login (8 horas)
JWT_COOKIE_NAME = "jwt_token"


class JWTService:
    @staticmethod
    def gerar_token(usuario):
        """
        Gera um token JWT assinado contendo os dados essenciais do usuário autenticado.
        """
        agora = datetime.now(timezone.utc)
        expiracao = agora + timedelta(hours=JWT_EXP_HOURS)

        payload = {
            "sub": usuario.get_email(),
            "usuario_email": usuario.get_email(),
            "usuario_nome": usuario.get_nome_exibicao(),
            "usuario_tipo": usuario.get_tipo(),
            "iat": agora,
            "exp": expiracao,
        }

        token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
        return token

    @staticmethod
    def decodificar_token(token):
        """
        Valida a assinatura e o tempo de expiração do token JWT.
        Retorna o dicionário (payload) se válido, ou None se inválido/expirado.
        """
        if not token:
            return None
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            # Token expirou
            return None
        except jwt.InvalidTokenError:
            # Token adulterado ou malformado
            return None

    @staticmethod
    def extrair_token_requisicao():
        """
        Busca o token JWT na requisição atual:
          1º) No cabeçalho HTTP `Authorization: Bearer <token>` (chamadas de API / fetch)
          2º) No cookie `jwt_token` enviado automaticamente pelo navegador
        """
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            return auth_header.split(" ", 1)[1].strip()

        return request.cookies.get(JWT_COOKIE_NAME)

    @staticmethod
    def anexar_cookie_jwt(response, token):
        """
        Grava o token JWT em um cookie HttpOnly na resposta HTTP.
        """
        response.set_cookie(
            JWT_COOKIE_NAME,
            token,
            max_age=JWT_EXP_HOURS * 3600,
            httponly=True,
            samesite="Lax",
            path="/",
        )
        return response

    @staticmethod
    def remover_cookie_jwt(response):
        """
        Remove o cookie do token JWT no logout ou quando expira.
        """
        response.delete_cookie(JWT_COOKIE_NAME, path="/")
        return response


def jwt_obrigatorio(f):
    """
    Decorator para proteger rotas no app.py exigindo um token JWT válido.
    Se não houver token válido, redireciona para a tela de login (/cadastro).
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = JWTService.extrair_token_requisicao()
        payload = JWTService.decodificar_token(token)
        if not payload:
            if request.is_json:
                return jsonify({"erro": "Token JWT ausente ou inválido."}), 401
            flash("Você precisa estar logado para acessar esta página.", "error")
            return redirect("/cadastro")
        g.jwt_payload = payload
        return f(*args, **kwargs)
    return decorated_function

