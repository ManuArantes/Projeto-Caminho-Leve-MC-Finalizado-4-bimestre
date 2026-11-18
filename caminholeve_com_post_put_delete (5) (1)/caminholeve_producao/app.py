# =====================================================================
#  app.py  —  PONTO DE ENTRADA DO SISTEMA (é este arquivo que você roda)
# =====================================================================
#  Aqui nasce a aplicação Flask. Este arquivo faz 3 coisas:
#    1) Cria o objeto `app` (o servidor web).
#    2) Cria uma instância de cada Controller.
#    3) Liga cada URL (rota) a um método do Controller.
#
#  ARQUITETURA EM CAMADAS (ótima para explicar na apresentação):
#
#    Navegador  ->  app.py (rota)  ->  Controller  ->  Service  ->  DAO  ->  Banco MySQL
#                                         |              |           |
#                                   recebe o pedido   regras de    comandos SQL
#                                   e decide a        negócio e    (SELECT/INSERT...)
#                                   resposta          validações
#                                   (HTML/redirect)
#    + Model: classes simples (Usuario, Forum, Relato, Artigo) que carregam os dados.
#    + Templates (HTML/Jinja): a parte visual que o usuário vê.
#
#  Para rodar:  python app.py   ->  abre em http://127.0.0.1:5000

import json
import os
# Importa do Flask: Flask (o app), render_template, redirect, session, request, flash, url_for, g e jsonify.
from flask import Flask, render_template, redirect, session, request, flash, url_for, g, jsonify
# Importa os 5 Controllers (um por assunto do site: artigos, usuários, fórum, relatos e admin).
from controllers.artigo_controller import ArtigoController
from controllers.usuario_controller import UsuarioController
from controllers.forum_controller import ForumController
from controllers.relato_controller import RelatoController
from controllers.admin_controller import AdminController
from services.feedback_service import FeedbackService
from services.jwt_service import JWTService, jwt_obrigatorio

# Cria a aplicação web. __name__ diz ao Flask onde estão as pastas templates/ e static/.
app = Flask(__name__)
# Chave usada para ASSINAR o cookie de sessão (session[...]) e as mensagens flash.
# Sem ela o login não funcionaria. ATENÇÃO: está escrita direto no código; em produção
# o ideal é guardar em variável de ambiente.
app.secret_key = "caminholeve_secret_key"

# -------------------- AUTENTICAÇÃO JWT (Middleware Global) --------------------
# Antes de cada requisição (@app.before_request), verificamos o token JWT enviado
# no cookie `jwt_token` ou no cabeçalho `Authorization: Bearer <token>`.
@app.before_request
def verificar_jwt_requisicao():
    if request.endpoint == "static":
        return

    token = JWTService.extrair_token_requisicao()
    payload = JWTService.decodificar_token(token)

    if payload:
        g.jwt_payload = payload
        # Mantém os dados do usuário autenticado sincronizados a partir do JWT validado
        session["usuario_email"] = payload.get("usuario_email")
        session["usuario_nome"] = payload.get("usuario_nome")
        session["usuario_tipo"] = payload.get("usuario_tipo")
    else:
        g.jwt_payload = None
        # Se não houver JWT válido (ou se expirou), remove qualquer estado de login
        session.pop("usuario_email", None)
        session.pop("usuario_nome", None)
        session.pop("usuario_tipo", None)

# Endpoint para consultar o status do token JWT atual (útil para testes e API)
@app.route("/auth/status")
def auth_status():
    if getattr(g, "jwt_payload", None):
        return jsonify({
            "autenticado": True,
            "jwt_payload": g.jwt_payload
        })
    return jsonify({"autenticado": False, "jwt_payload": None}), 401

# -------------------- INTERNACIONALIZAÇÃO (i18n via JSON) --------------------
# Idiomas suportados: Português (pt), Espanhol (es) e Inglês (en)
TRANSLATIONS_DIR = os.path.join(os.path.dirname(__file__), "translations")
SUPPORTED_LANGUAGES = ["pt", "es", "en"]
TRANSLATIONS = {}

def carregar_traducoes():
    for lang in SUPPORTED_LANGUAGES:
        caminho = os.path.join(TRANSLATIONS_DIR, f"{lang}.json")
        if os.path.exists(caminho):
            with open(caminho, "r", encoding="utf-8") as f:
                TRANSLATIONS[lang] = json.load(f)
        else:
            TRANSLATIONS[lang] = {}

carregar_traducoes()

@app.context_processor
def inject_locale():
    lang = session.get("lang", "pt")
    if lang not in SUPPORTED_LANGUAGES:
        lang = "pt"
    
    def t(key, default=None):
        return (
            TRANSLATIONS.get(lang, {}).get(key)
            or TRANSLATIONS.get("pt", {}).get(key)
            or default
            or key
        )
    
    return {
        "current_lang": lang,
        "t": t,
        "trans": TRANSLATIONS.get(lang, TRANSLATIONS.get("pt", {})),
        "supported_languages": SUPPORTED_LANGUAGES
    }

# Rota para alternar o idioma do site
@app.route("/mudar-idioma/<lang>")
def mudar_idioma(lang):
    if lang in SUPPORTED_LANGUAGES:
        session["lang"] = lang
    referrer = request.referrer
    if referrer and request.host in referrer:
        return redirect(referrer)
    return redirect("/principal")

artigo_controller = ArtigoController()
usuario_controller = UsuarioController()
forum_controller = ForumController()
relato_controller = RelatoController()
admin_controller = AdminController()

# -------------------- PÁGINAS PÚBLICAS --------------------
# @app.route("URL") liga uma URL à função logo abaixo dela.
# A raiz do site ("/") apenas redireciona para a página principal.
@app.route("/")
def raiz():
    return redirect("/principal")

# Página inicial: 'O que é Miastenia Congênita?'. É conteúdo estático, então renderiza o template direto, sem Controller.
@app.route("/principal")
def principal():
    return render_template("principal.html")

# Página 'Minha História' (linha do tempo). Também estática.
@app.route("/minhahistoria")
def minhahistoria():
    return render_template("minhahistoria.html")

# -------------------- ACOLHIMENTO: FÓRUM + RELATOS --------------------
# Página com duas abas (Fórum e Relatos). O Controller busca os dados no banco antes de renderizar.
@app.route("/acolhimento")
def acolhimento():
    return forum_controller.exibir_acolhimento()

# POST: publica uma nova mensagem no fórum (vem do formulário da página de acolhimento).
@app.route("/forum/post/novo", methods=["POST"])
def forum_post_novo():
    return forum_controller.criar_post()

# POST: publica uma RESPOSTA dentro de uma mensagem do fórum.
@app.route("/forum/resposta/nova", methods=["POST"])
def forum_resposta_nova():
    return forum_controller.criar_resposta()

# Curtir/descurtir um post. <int:forum_id> captura o número da URL e entrega à função. (Aceita GET porque o botão de curtir é um link <a>.)
@app.route("/forum/post/curtir/<int:forum_id>", methods=["POST", "GET"])
def forum_post_curtir(forum_id):
    return forum_controller.curtir_post(forum_id)

# Curtir/descurtir uma resposta do fórum.
@app.route("/forum/resposta/curtir/<int:resposta_id>", methods=["POST", "GET"])
def forum_resposta_curtir(resposta_id):
    return forum_controller.curtir_resposta(resposta_id)

# Denunciar uma resposta. Com 3 denúncias ela é ocultada automaticamente.
@app.route("/forum/resposta/denunciar/<int:resposta_id>", methods=["POST", "GET"])
def forum_resposta_denunciar(resposta_id):
    return forum_controller.denunciar_resposta(resposta_id)

# Denunciar um post. Com 3 denúncias ele some para os outros usuários.
@app.route("/forum/post/denunciar/<int:forum_id>", methods=["POST", "GET"])
def forum_post_denunciar(forum_id):
    return forum_controller.denunciar_post(forum_id)

# -------------------- RELATOS (histórias pessoais) --------------------
# POST: publica um novo relato.
@app.route("/relato/novo", methods=["POST"])
def relato_novo():
    return relato_controller.criar_relato()

# Curtir/descurtir um relato (no site aparece como 'pessoas se identificaram').
@app.route("/relato/curtir/<int:relato_id>", methods=["POST", "GET"])
def relato_curtir(relato_id):
    return relato_controller.curtir_relato(relato_id)

# Denunciar um relato (3 denúncias = oculto).
@app.route("/relato/denunciar/<int:relato_id>", methods=["POST", "GET"])
def relato_denunciar(relato_id):
    return relato_controller.denunciar_relato(relato_id)

# -------------------- ARTIGOS MÉDICOS --------------------
# Lista os artigos já APROVADOS e, se o usuário tiver um token JWT válido, mostra também as sugestões dele.
# (Para exigir login obrigatório nesta rota, basta descomentar @jwt_obrigatorio abaixo.)
@app.route("/artigos")
# @jwt_obrigatorio
def artigos():
    return artigo_controller.artigos()

# POST: usuário autenticado via JWT sugere um artigo. Ele entra como 'pendente' até um ADM aprovar.
@app.route("/artigo/sugerir", methods=["POST"])
@jwt_obrigatorio
def artigo_sugerir():
    return artigo_controller.sugerir_artigo()

# GET (API JSON pura para integração com React — sem Jinja2):
# Retorna os artigos médicos aprovados em formato JSON (suporta ?page=1&per_page=3 opcional).
@app.route("/api/artigos", methods=["GET"])
def api_artigos():
    return artigo_controller.listar_artigos_json()

# POST: cria uma sugestão de artigo em formato JSON (usuário autenticado).
@app.route("/api/artigos", methods=["POST"])
def api_criar_artigo():
    return artigo_controller.criar_artigo_json()

# PUT: atualiza os dados de um artigo (somente ADM).
@app.route("/api/artigos/<int:artigo_id>", methods=["PUT"])
def api_atualizar_artigo(artigo_id):
    return artigo_controller.atualizar_artigo_json(artigo_id)

# DELETE: remove um artigo (somente ADM).
@app.route("/api/artigos/<int:artigo_id>", methods=["DELETE"])
def api_excluir_artigo(artigo_id):
    return artigo_controller.excluir_artigo_json(artigo_id)

# ==========================================
# PAINEL ADMINISTRATIVO (ADM)
# ==========================================
# Tela principal do painel do administrador (estatísticas + listas de moderação). Só ADM consegue entrar — a checagem fica no AdminController.
@app.route("/admin")
def admin_painel():
    return admin_controller.exibir_painel()

# ADM: ativa/desativa um usuário (bloqueia o login dele).
@app.route("/admin/usuario/status/<email>", methods=["POST", "GET"])
def admin_usuario_status(email):
    return admin_controller.alternar_usuario_status(email)

# ADM: promove um usuário a ADM ou rebaixa para Portador.
@app.route("/admin/usuario/tipo/<email>", methods=["POST", "GET"])
def admin_usuario_tipo(email):
    return admin_controller.alternar_usuario_tipo(email)

# ADM — moderação de POSTS do fórum: 'limpar' = descartar as denúncias e reabilitar o post.
@app.route("/admin/forum/limpar/<int:forum_id>", methods=["POST", "GET"])
def admin_forum_limpar(forum_id):
    return admin_controller.limpar_denuncias_post(forum_id)

# ADM: oculta/mostra manualmente um post.
@app.route("/admin/forum/ocultar/<int:forum_id>", methods=["POST", "GET"])
def admin_forum_ocultar(forum_id):
    return admin_controller.alternar_ocultar_post(forum_id)

# ADM: exclui o post de vez (junto com respostas e curtidas).
@app.route("/admin/forum/excluir/<int:forum_id>", methods=["POST", "GET"])
def admin_forum_excluir(forum_id):
    return admin_controller.excluir_post(forum_id)

# ADM — moderação de RESPOSTAS: ativa/inativa uma resposta.
@app.route("/admin/resposta/status/<int:resposta_id>", methods=["POST", "GET"])
def admin_resposta_status(resposta_id):
    return admin_controller.alternar_resposta_status(resposta_id)

# ADM: descarta denúncias da resposta e reativa.
@app.route("/admin/resposta/limpar/<int:resposta_id>", methods=["POST", "GET"])
def admin_resposta_limpar(resposta_id):
    return admin_controller.limpar_denuncias_resposta(resposta_id)

# ADM: exclui a resposta permanentemente.
@app.route("/admin/resposta/excluir/<int:resposta_id>", methods=["POST", "GET"])
def admin_resposta_excluir(resposta_id):
    return admin_controller.excluir_resposta(resposta_id)

# ADM — moderação de RELATOS: descarta denúncias.
@app.route("/admin/relato/limpar/<int:relato_id>", methods=["POST", "GET"])
def admin_relato_limpar(relato_id):
    return admin_controller.limpar_denuncias_relato(relato_id)

# ADM: oculta/mostra um relato.
@app.route("/admin/relato/ocultar/<int:relato_id>", methods=["POST", "GET"])
def admin_relato_ocultar(relato_id):
    return admin_controller.alternar_ocultar_relato(relato_id)

# ADM: exclui o relato permanentemente.
@app.route("/admin/relato/excluir/<int:relato_id>", methods=["POST", "GET"])
def admin_relato_excluir(relato_id):
    return admin_controller.excluir_relato(relato_id)

# ADM — moderação de ARTIGOS: aprova (vira público).
@app.route("/admin/artigo/aprovar/<int:artigo_id>", methods=["POST", "GET"])
def admin_artigo_aprovar(artigo_id):
    return admin_controller.aprovar_artigo(artigo_id)

# ADM: rejeita a sugestão (status 'R').
@app.route("/admin/artigo/rejeitar/<int:artigo_id>", methods=["POST", "GET"])
def admin_artigo_rejeitar(artigo_id):
    return admin_controller.rejeitar_artigo(artigo_id)

# ADM: apaga o artigo.
@app.route("/admin/artigo/excluir/<int:artigo_id>", methods=["POST", "GET"])
def admin_artigo_excluir(artigo_id):
    return admin_controller.excluir_artigo(artigo_id)

# ADM: cadastra um artigo já aprovado, direto pelo painel.
@app.route("/admin/artigo/novo", methods=["POST"])
def admin_artigo_novo():
    return admin_controller.cadastrar_artigo()

# Página de Referências bibliográficas e LGPD (estática).
@app.route("/referencia")
def referencia():
    return render_template("referencia.html")

# -------------------- FEEDBACK DA COMUNIDADE (JSON) --------------------
# Rota pública de feedback (redireciona para a seção de feedback em referências)
@app.route("/feedback")
def feedback():
    return redirect(url_for("referencia") + "#feedback")

# POST: processa e armazena o feedback no feedbacks.json
@app.route("/feedback/enviar", methods=["POST"])
def feedback_enviar():
    nome = request.form.get("nome")
    texto = request.form.get("texto")
    try:
        FeedbackService.adicionar_feedback(nome, texto)
        flash("Seu feedback foi enviado com sucesso aos administradores! Muito obrigado.", "success")
    except Exception as e:
        flash(str(e), "error")
    return redirect(url_for("referencia") + "#feedback")

# ADM: excluir feedback do painel
@app.route("/admin/feedback/excluir/<int:feedback_id>", methods=["POST"])
def admin_feedback_excluir(feedback_id):
    return admin_controller.excluir_feedback(feedback_id)

# -------------------- CONTAS DE USUÁRIO --------------------
# Mostra a tela com as abas 'Entrar' e 'Criar Conta'.
@app.route("/cadastro")
def cadastro():
    return render_template("cadastro.html")


# POST: processa o formulário 'Criar Conta'.
@app.route("/realizar_cadastro", methods=["POST"])
def realizar_cadastro():
    return usuario_controller.realizar_cadastro()

# POST: processa o formulário 'Entrar' e grava os dados do usuário na session.
@app.route("/login", methods=["POST"])
def login():
    return usuario_controller.login()

# Limpa a session (desloga) e volta para a página principal.
@app.route("/logout")
def logout():
    return usuario_controller.logout()

# Mostra a página 'Meu Perfil' (exige login).
@app.route("/perfil")
def perfil():
    return usuario_controller.exibir_perfil()

# POST: salva nome, cidade, estado e nascimento.
@app.route("/perfil/atualizar", methods=["POST"])
def perfil_atualizar():
    return usuario_controller.atualizar_dados()

# POST: troca a senha (pede a senha atual).
@app.route("/perfil/senha", methods=["POST"])
def perfil_senha():
    return usuario_controller.atualizar_senha()

# ==========================================
# FLUXO DE RECUPERAÇÃO DE SENHA (SEM E-MAIL)
# ==========================================
# -------------------- RECUPERAÇÃO DE SENHA (sem e-mail) --------------------
# Fluxo em 3 passos, usando PERGUNTAS DE SEGURANÇA no lugar de e-mail:
#   1) /recuperar_senha          -> usuário informa o e-mail
#   2) /recuperar_senha/perguntas -> responde 3 perguntas (cidade, UF, nascimento)
#   3) /recuperar_senha/nova_senha -> define a nova senha
# Errou 3 vezes? A conta é bloqueada e só um ADM desbloqueia.
# methods=["GET","POST"]: a mesma URL mostra a tela (GET) e processa o envio (POST).
@app.route("/recuperar_senha", methods=["GET", "POST"])
def recuperar_senha():
    return usuario_controller.recuperar_senha_inicio()

# Passo 2: mostra as perguntas (GET) e confere as respostas (POST).
@app.route("/recuperar_senha/perguntas", methods=["GET", "POST"])
def recuperar_senha_perguntas():
    return usuario_controller.recuperar_senha_perguntas()

# Passo 3: só abre se o passo 2 foi aprovado (flag na session).
@app.route("/recuperar_senha/nova_senha", methods=["GET", "POST"])
def recuperar_senha_nova_senha():
    return usuario_controller.recuperar_senha_nova()

# Tela exibida quando a conta foi bloqueada por excesso de erros.
@app.route("/recuperar_senha/bloqueado")
def recuperar_senha_bloqueado():
    return usuario_controller.recuperar_senha_bloqueado()



# Só executa quando você roda `python app.py` diretamente.
# debug=True liga o recarregamento automático e mostra erros detalhados (use só em desenvolvimento).
if __name__ == "__main__":
    app.run(debug=True)
