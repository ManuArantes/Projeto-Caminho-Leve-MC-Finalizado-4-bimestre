# forum_controller.py — CONTROLLER DO FÓRUM
# Cuida da página /acolhimento (que mostra Fórum E Relatos) e das ações do fórum:
# publicar, responder, curtir e denunciar. Padrão repetido em quase todos os métodos:
#   1) pega o e-mail do usuário na session  2) se não estiver logado -> flash + vai para /cadastro
#   3) chama o Service dentro de try/except  4) redireciona de volta para a aba do fórum.
from flask import render_template, request, redirect, flash, session
from services.forum_services import ForumService
from services.relato_services import RelatoService

# Controller do fórum.
class ForumController:
    # Usa DOIS services: ForumService (posts/respostas) e RelatoService (a mesma página também lista os relatos).
    def __init__(self):
        self.service = ForumService()
        self.relato_service = RelatoService()

    # Monta a página de Acolhimento: busca posts do fórum e relatos e entrega os dois ao template acolhimento.html.
    # Cada busca tem seu próprio try/except: se uma falhar, a outra ainda aparece (lista vazia + mensagem de erro).
    def exibir_acolhimento(self):
        usuario_email = session.get("usuario_email")
        try:
            posts = self.service.listar_forum(usuario_email)
        except Exception as e:
            flash(f"Erro ao carregar o fórum: {str(e)}", "error")
            posts = []

        try:
            relatos = self.relato_service.listar_relatos(usuario_email)
        except Exception as e:
            flash(f"Erro ao carregar os relatos: {str(e)}", "error")
            relatos = []

        return render_template("acolhimento.html", posts=posts, relatos=relatos)

    # Publica uma nova mensagem. Exige login.
    def criar_post(self):
        usuario_email = session.get("usuario_email")
        if not usuario_email:
            flash("Você precisa estar logado para publicar no fórum.", "error")
            return redirect("/cadastro")
            
        texto = request.form.get("texto")
        try:
            self.service.criar_post(usuario_email, texto)
            flash("Mensagem publicada com sucesso!", "success")
        except Exception as e:
            flash(str(e), "error")
            
        return redirect("/acolhimento?tab=forum")

    # Publica uma resposta; 'forum_id' vem de um campo oculto (<input type="hidden">) do formulário.
    def criar_resposta(self):
        usuario_email = session.get("usuario_email")
        if not usuario_email:
            flash("Você precisa estar logado para responder.", "error")
            return redirect("/cadastro")
            
        forum_id = request.form.get("forum_id")
        texto = request.form.get("texto")
        try:
            self.service.criar_resposta(forum_id, usuario_email, texto)
            flash("Resposta publicada com sucesso!", "success")
        except Exception as e:
            flash(str(e), "error")
            
        return redirect("/acolhimento?tab=forum")

    # Curtir/descurtir post (funciona como 'liga/desliga'). Exige login.
    def curtir_post(self, forum_id):
        usuario_email = session.get("usuario_email")
        if not usuario_email:
            flash("Você precisa estar logado para curtir.", "error")
            return redirect("/cadastro")
            
        try:
            self.service.curtir_post(forum_id, usuario_email)
        except Exception as e:
            flash(str(e), "error")
            
        return redirect("/acolhimento?tab=forum")

    # Curtir/descurtir resposta.
    def curtir_resposta(self, resposta_id):
        usuario_email = session.get("usuario_email")
        if not usuario_email:
            flash("Você precisa estar logado para curtir.", "error")
            return redirect("/cadastro")
            
        try:
            self.service.curtir_resposta(resposta_id, usuario_email)
        except Exception as e:
            flash(str(e), "error")
            
        return redirect("/acolhimento?tab=forum")

    # Denuncia uma resposta. O Service devolve True se esta foi a 3ª denúncia e a resposta foi ocultada — a mensagem muda conforme isso.
    def denunciar_resposta(self, resposta_id):
        usuario_email = session.get("usuario_email")
        if not usuario_email:
            flash("Você precisa estar logado para denunciar.", "error")
            return redirect("/cadastro")
            
        try:
            inativada = self.service.denunciar_resposta(resposta_id, usuario_email)
            if inativada:
                flash("Resposta ocultada após receber 3 denúncias.", "success")
            else:
                flash("Resposta denunciada com sucesso.", "success")
        except Exception as e:
            flash(str(e), "error")
            
        return redirect("/acolhimento?tab=forum")

    # Denuncia um post (mesma lógica: True = ocultado após 3 denúncias).
    def denunciar_post(self, forum_id):
        usuario_email = session.get("usuario_email")
        if not usuario_email:
            flash("Você precisa estar logado para denunciar.", "error")
            return redirect("/cadastro")
            
        try:
            ocultado = self.service.denunciar_post(forum_id, usuario_email)
            if ocultado:
                flash("Publicação ocultada após receber 3 denúncias.", "success")
            else:
                flash("Publicação denunciada com sucesso.", "success")
        except Exception as e:
            flash(str(e), "error")
            
        return redirect("/acolhimento?tab=forum")
