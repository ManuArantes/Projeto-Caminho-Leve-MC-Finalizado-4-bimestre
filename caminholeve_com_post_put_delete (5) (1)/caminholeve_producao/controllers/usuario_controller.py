# request = dados enviados pelo formulário | session = "memória" do usuário logado (cookie assinado)
# flash = mensagem temporária (sucesso/erro) | redirect = manda o navegador para outra URL
# usuario_controller.py — CONTROLLER DE USUÁRIO
# O Controller é a "porta de entrada" de cada pedido do navegador. Ele:
#   1) LÊ os dados do pedido (request.form = campos do formulário, session = quem está logado)
#   2) CHAMA o Service para aplicar as regras de negócio
#   3) DECIDE a resposta: mostrar uma página (render_template) ou redirecionar (redirect)
#   4) Avisa o usuário com mensagens flash (aparecem no topo da página, vide base.html)
# Aqui: cadastro, login, logout, perfil, troca de senha e recuperação de senha.
from flask import render_template, request, redirect, flash, session, make_response, jsonify
from services.usuario_services import UsuarioService
from services.jwt_service import JWTService

# Agrupa todas as ações ligadas à conta do usuário.
class UsuarioController:
    # Ao criar o controller, ele já cria o Service que vai usar (Controller -> Service).
    def __init__(self):
        self.service = UsuarioService()

    # CADASTRO: chamado quando o usuário envia o formulário 'Criar Conta'.
    # Fluxo: pega os campos -> confere se as senhas batem -> pede ao Service para cadastrar -> avisa o resultado.
    def realizar_cadastro(self):
        nome = request.form.get("nome")
        nickname = request.form.get("nickname")
        email = request.form.get("email")
        cidade = request.form.get("cidade")
        estado = request.form.get("estado")
        nascimento = request.form.get("nascimento")
        perfil = request.form.get("perfil")
        senha = request.form.get("senha")
        confirmar_senha = request.form.get("confirmar_senha")

        # Validação de senhas coincidentes
        if senha != confirmar_senha:
            flash("As senhas não coincidem!", "error")
            return redirect("/cadastro?tab=cadastro")

        # Mapeamento do perfil (Portador, Familiar, Outro) para tipo enum('Portador','Outros')
        tipo = "Portador" if perfil == "Portador" else "Outros"

        # Formatar nascimento (se vazio enviar None)
        nascimento_val = nascimento if nascimento else None

        try:
            self.service.cadastrar(
                email=email,
                nome=nome,
                nickname=nickname,
                cidade=cidade if cidade else None,
                estado=estado if estado else None,
                nascimento=nascimento_val,
                tipo=tipo,
                senha=senha
            )
            flash("Cadastro realizado com sucesso! Faça login abaixo.", "success")
            return redirect("/cadastro")
        except Exception as e:
            flash(str(e), "error")
            return redirect("/cadastro?tab=cadastro")

    # LOGIN (COM JWT): recebe e-mail e senha (via formulário HTML ou JSON).
    # O Service confere as credenciais; se estiver tudo certo, geramos um token JWT
    # assinado (HS256) e o enviamos em um cookie HttpOnly (`jwt_token`).
    def login(self):
        dados_json = request.get_json(silent=True) if request.is_json else None
        email = dados_json.get("email") if dados_json else request.form.get("email")
        senha = dados_json.get("senha") if dados_json else request.form.get("senha")

        try:
            usuario = self.service.autenticar(email, senha)

            # Gera o token JWT assinado contendo email, nome de exibição, tipo e expiração
            token = JWTService.gerar_token(usuario)

            # Sincroniza os dados na session para os templates Jinja2 renderizarem imediatamente
            session["usuario_email"] = usuario.get_email()
            session["usuario_nome"] = usuario.get_nome_exibicao()
            session["usuario_tipo"] = usuario.get_tipo()

            if request.is_json:
                resp = make_response(jsonify({
                    "sucesso": True,
                    "mensagem": f"Bem-vindo(a), {usuario.get_nome_exibicao()}!",
                    "token": token,
                    "usuario": {
                        "email": usuario.get_email(),
                        "nome": usuario.get_nome_exibicao(),
                        "tipo": usuario.get_tipo(),
                    },
                }))
                return JWTService.anexar_cookie_jwt(resp, token)

            flash(f"Bem-vindo(a), {usuario.get_nome_exibicao()}! 🫶", "success")
            resp = make_response(redirect("/principal"))
            return JWTService.anexar_cookie_jwt(resp, token)
        except Exception as e:
            if request.is_json:
                return jsonify({"sucesso": False, "erro": str(e)}), 401
            flash(str(e), "error")
            return redirect("/cadastro")

    # LOGOUT: limpa a session e remove o cookie do token JWT, encerrando a autenticação.
    def logout(self):
        lang = session.get("lang")
        session.clear()
        if lang:
            session["lang"] = lang
        flash("Você saiu do sistema.", "success")
        resp = make_response(redirect("/principal"))
        return JWTService.remover_cookie_jwt(resp)

    # PERFIL: só mostra a página se houver usuário na session (exige login). Busca os dados no banco e envia para perfil.html.
    def exibir_perfil(self):
        email = session.get("usuario_email")
        if not email:
            flash("Você precisa estar logado para acessar seu perfil.", "error")
            return redirect("/cadastro")

        try:
            usuario = self.service.buscar_por_email(email)
            if not usuario:
                flash("Usuário não encontrado.", "error")
                return redirect("/principal")
            return render_template("perfil.html", usuario=usuario)
        except Exception as e:
            flash(str(e), "error")
            return redirect("/principal")

    # Salva os dados pessoais (o e-mail não muda: ele é a chave do usuário). Atualiza também o nome guardado na session.
    def atualizar_dados(self):
        email = session.get("usuario_email")
        if not email:
            flash("Sessão expirada. Faça login novamente.", "error")
            return redirect("/cadastro")

        nome = request.form.get("nome")
        nickname = request.form.get("nickname")
        cidade = request.form.get("cidade")
        estado = request.form.get("estado")
        nascimento = request.form.get("nascimento")

        try:
            usuario_atualizado = self.service.atualizar_dados(
                email=email,
                nome=nome,
                nickname=nickname,
                cidade=cidade,
                estado=estado,
                nascimento=nascimento
            )
            session["usuario_nome"] = usuario_atualizado.get_nome_exibicao()
            novo_token = JWTService.gerar_token(usuario_atualizado)
            flash("Seus dados foram atualizados com sucesso! ✨", "success")
            resp = make_response(redirect("/perfil"))
            return JWTService.anexar_cookie_jwt(resp, novo_token)
        except Exception as e:
            flash(str(e), "error")

        return redirect("/perfil")

    # TROCA DE SENHA (usuário logado): exige a senha atual, a nova e a confirmação.
    def atualizar_senha(self):
        email = session.get("usuario_email")
        if not email:
            flash("Sessão expirada. Faça login novamente.", "error")
            return redirect("/cadastro")

        senha_atual = request.form.get("senha_atual")
        nova_senha = request.form.get("nova_senha")
        confirmar_nova_senha = request.form.get("confirmar_nova_senha")

        try:
            self.service.atualizar_senha(
                email=email,
                senha_atual=senha_atual,
                nova_senha=nova_senha,
                confirmar_nova_senha=confirmar_nova_senha
            )
            flash("Sua senha foi alterada com sucesso! 🔒", "success")
        except Exception as e:
            flash(str(e), "error")

        return redirect("/perfil")

    # ========================================================
    # FLUXO DE RECUPERAÇÃO DE SENHA POR PERGUNTAS DE SEGURANÇA
    # ========================================================
    # RECUPERAÇÃO — PASSO 1: usuário informa o e-mail.
    # GET  -> só mostra o formulário.  POST -> verifica se o e-mail existe e se a conta não está bloqueada.
    # O e-mail fica em session['recuperar_email'] para os próximos passos.
    def recuperar_senha_inicio(self):
        if request.method == "GET":
            return render_template("recuperar_senha.html")

        email = request.form.get("email")
        if not email or not email.strip():
            flash("Informe seu e-mail cadastrado.", "error")
            return render_template("recuperar_senha.html")

        email = email.strip()
        try:
            perguntas, usuario = self.service.obter_perguntas_seguranca(email)
            session["recuperar_email"] = email
            session.pop("recuperar_autorizado", None)
            return redirect("/recuperar_senha/perguntas")
        except Exception as e:
            flash(str(e), "error")
            if "bloqueada" in str(e).lower():
                return redirect("/recuperar_senha/bloqueado")
            return render_template("recuperar_senha.html", email_informado=email)

    # RECUPERAÇÃO — PASSO 2: perguntas de segurança.
    # GET  -> mostra as 3 perguntas e quantas tentativas restam.
    # POST -> compara as respostas com o cadastro; se acertar tudo, libera o passo 3.
    def recuperar_senha_perguntas(self):
        email = session.get("recuperar_email")
        if not email:
            flash("Por favor, informe seu e-mail para iniciar a recuperação.", "error")
            return redirect("/recuperar_senha")

        try:
            perguntas, usuario = self.service.obter_perguntas_seguranca(email)
        except Exception as e:
            flash(str(e), "error")
            return redirect("/recuperar_senha/bloqueado")

        tentativas_restantes = 3 - (usuario.get_erros_recuperacao() or 0)

        if request.method == "GET":
            return render_template(
                "recuperar_senha_perguntas.html",
                email=email,
                perguntas=perguntas,
                tentativas_restantes=tentativas_restantes
            )

        # POST: Coleta as respostas do formulário
        respostas = {}
        for p in perguntas:
            campo = p["campo"]
            respostas[campo] = request.form.get(campo, "").strip()

        sucesso, erros, msg = self.service.validar_respostas_seguranca(email, respostas)

        if sucesso:
            session["recuperar_autorizado"] = True
            flash("Identidade confirmada com sucesso! Digite sua nova senha abaixo. ✨", "success")
            return redirect("/recuperar_senha/nova_senha")
        else:
            if erros >= 3:
                session.pop("recuperar_email", None)
                flash(msg, "error")
                return redirect("/recuperar_senha/bloqueado")
            else:
                flash(msg, "error")
                return redirect("/recuperar_senha/perguntas")

    # RECUPERAÇÃO — PASSO 3: define a nova senha.
    # Proteção: sem e-mail E sem a marca 'autorizado' na session o acesso é negado
    # (ninguém pula o passo 2 digitando a URL direto).
    def recuperar_senha_nova(self):
        email = session.get("recuperar_email")
        autorizado = session.get("recuperar_autorizado")

        if not email or not autorizado:
            flash("Acesso não autorizado. Inicie a recuperação de senha novamente.", "error")
            return redirect("/recuperar_senha")

        if request.method == "GET":
            return render_template("recuperar_senha_nova.html", email=email)

        nova_senha = request.form.get("nova_senha")
        confirmar_nova_senha = request.form.get("confirmar_nova_senha")

        try:
            self.service.redefinir_senha_recuperacao(email, nova_senha, confirmar_nova_senha)
            session.pop("recuperar_email", None)
            session.pop("recuperar_autorizado", None)
            flash("Senha redefinida com sucesso! Você já pode entrar com sua nova senha. 🫶", "success")
            return redirect("/cadastro")
        except Exception as e:
            flash(str(e), "error")
            return render_template("recuperar_senha_nova.html", email=email)

    # Tela informando que a conta foi bloqueada e que é preciso falar com o administrador.
    def recuperar_senha_bloqueado(self):
        return render_template("recuperar_senha_bloqueado.html")
