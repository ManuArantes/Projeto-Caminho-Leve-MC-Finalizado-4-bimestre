# admin_controller.py — CONTROLLER DO PAINEL ADMINISTRATIVO
# Todas as ações de moderação: usuários, fórum, respostas, relatos e artigos.
# REGRA DE OURO: todo método começa com _verificar_adm(). Se o usuário não for ADM,
# é expulso para /principal. Assim ninguém comum acessa o painel nem digitando a URL.
# Depois de cada ação, redireciona para a aba certa do painel (?tab=...).
from flask import render_template, request, redirect, flash, session
from services.admin_services import AdminService
from services.feedback_service import FeedbackService

class AdminController:
    def __init__(self):
        self.service = AdminService()

    # GUARDA DE SEGURANÇA: lê session['usuario_tipo'] e só libera se for 'ADM'.
    # O _ no início do nome é convenção Python para 'método de uso interno da classe'.
    def _verificar_adm(self):
        if session.get("usuario_tipo") != "ADM":
            flash("Acesso negado! Esta área é exclusiva para Administradores.", "error")
            return False
        return True

    # Abre o painel: o Service reúne estatísticas e listas e tudo vai para admin.html. `**dados` espalha o dicionário como variáveis do template.
    def exibir_painel(self):
        if not self._verificar_adm():
            return redirect("/principal")

        try:
            dados = self.service.obter_painel_dados()
            dados["feedbacks"] = FeedbackService.listar_feedbacks()
            return render_template("admin.html", **dados)
        except Exception as e:
            flash(f"Erro ao carregar o painel administrativo: {str(e)}", "error")
            return redirect("/principal")

    # Ativa/desativa um usuário. Trava de segurança: o ADM NÃO pode desativar a si mesmo.
    def alternar_usuario_status(self, email):
        if not self._verificar_adm():
            return redirect("/principal")
        try:
            if email == session.get("usuario_email"):
                flash("Você não pode desativar sua própria conta de administrador!", "error")
            else:
                novo_status = self.service.alternar_status_usuario(email)
                msg = "ativado" if novo_status == "S" else "desativado"
                flash(f"Usuário {email} foi {msg} com sucesso.", "success")
        except Exception as e:
            flash(str(e), "error")
        return redirect("/admin?tab=usuarios")

    # Promove/rebaixa um usuário. Trava: o ADM não pode mudar o próprio privilégio (evita ficar sem nenhum administrador).
    def alternar_usuario_tipo(self, email):
        if not self._verificar_adm():
            return redirect("/principal")
        try:
            if email == session.get("usuario_email"):
                flash("Você não pode alterar seu próprio privilégio de administrador!", "error")
            else:
                novo_tipo = self.service.alternar_tipo_usuario(email)
                flash(f"Privilégio do usuário {email} alterado para {novo_tipo}.", "success")
        except Exception as e:
            flash(str(e), "error")
        return redirect("/admin?tab=usuarios")

    # ----- MODERAÇÃO DE POSTS DO FÓRUM -----
    # Fórum
    # Descarta as denúncias e devolve a visibilidade ao post.
    def limpar_denuncias_post(self, forum_id):
        if not self._verificar_adm():
            return redirect("/principal")
        try:
            self.service.limpar_denuncias_post(forum_id)
            flash("Denúncias do post descartadas e publicação reabilitada.", "success")
        except Exception as e:
            flash(str(e), "error")
        return redirect("/admin?tab=denuncias-forum")

    # Oculta/mostra o post manualmente.
    def alternar_ocultar_post(self, forum_id):
        if not self._verificar_adm():
            return redirect("/principal")
        try:
            self.service.alternar_ocultacao_post(forum_id)
            flash("Status de visibilidade do post atualizado.", "success")
        except Exception as e:
            flash(str(e), "error")
        return redirect("/admin?tab=denuncias-forum")

    # Exclusão definitiva (post + respostas + curtidas + denúncias).
    def excluir_post(self, forum_id):
        if not self._verificar_adm():
            return redirect("/principal")
        try:
            self.service.excluir_post(forum_id)
            flash("Post e todas as suas respostas foram excluídos permanentemente.", "success")
        except Exception as e:
            flash(str(e), "error")
        return redirect("/admin?tab=denuncias-forum")

    # ----- MODERAÇÃO DE RESPOSTAS -----
    # Respostas
    # Inativa/reativa a resposta (campo ativo S/N).
    def alternar_resposta_status(self, resposta_id):
        if not self._verificar_adm():
            return redirect("/principal")
        try:
            self.service.alternar_status_resposta(resposta_id)
            flash("Visibilidade da resposta alterada.", "success")
        except Exception as e:
            flash(str(e), "error")
        return redirect("/admin?tab=denuncias-respostas")

    def limpar_denuncias_resposta(self, resposta_id):
        if not self._verificar_adm():
            return redirect("/principal")
        try:
            self.service.limpar_denuncias_resposta(resposta_id)
            flash("Denúncias da resposta limpas e status reativado.", "success")
        except Exception as e:
            flash(str(e), "error")
        return redirect("/admin?tab=denuncias-respostas")

    def excluir_resposta(self, resposta_id):
        if not self._verificar_adm():
            return redirect("/principal")
        try:
            self.service.excluir_resposta(resposta_id)
            flash("Resposta excluída permanentemente.", "success")
        except Exception as e:
            flash(str(e), "error")
        return redirect("/admin?tab=denuncias-respostas")

    # ----- MODERAÇÃO DE RELATOS -----
    # Relatos
    # Descarta denúncias do relato.
    def limpar_denuncias_relato(self, relato_id):
        if not self._verificar_adm():
            return redirect("/principal")
        try:
            self.service.limpar_denuncias_relato(relato_id)
            flash("Denúncias do relato descartadas e publicação restaurada.", "success")
        except Exception as e:
            flash(str(e), "error")
        return redirect("/admin?tab=denuncias-relatos")

    def alternar_ocultar_relato(self, relato_id):
        if not self._verificar_adm():
            return redirect("/principal")
        try:
            self.service.alternar_ocultacao_relato(relato_id)
            flash("Status de visibilidade do relato atualizado.", "success")
        except Exception as e:
            flash(str(e), "error")
        return redirect("/admin?tab=denuncias-relatos")

    def excluir_relato(self, relato_id):
        if not self._verificar_adm():
            return redirect("/principal")
        try:
            self.service.excluir_relato(relato_id)
            flash("Relato excluído permanentemente.", "success")
        except Exception as e:
            flash(str(e), "error")
        return redirect("/admin?tab=denuncias-relatos")

    # ----- MODERAÇÃO DE ARTIGOS -----
    # Artigos Médicos
    # Aprova: revisado='1' e grava QUEM aprovou (e-mail do ADM na session).
    def aprovar_artigo(self, artigo_id):
        if not self._verificar_adm():
            return redirect("/principal")
        try:
            admin_email = session.get("usuario_email")
            self.service.aprovar_artigo(artigo_id, admin_email)
            flash("Artigo aprovado e publicado na lista pública!", "success")
        except Exception as e:
            flash(str(e), "error")
        return redirect("/admin?tab=artigos")

    # Rejeita: revisado='R'.
    def rejeitar_artigo(self, artigo_id):
        if not self._verificar_adm():
            return redirect("/principal")
        try:
            admin_email = session.get("usuario_email")
            self.service.rejeitar_artigo(artigo_id, admin_email)
            flash("Indicação de artigo rejeitada.", "success")
        except Exception as e:
            flash(str(e), "error")
        return redirect("/admin?tab=artigos")

    def excluir_artigo(self, artigo_id):
        if not self._verificar_adm():
            return redirect("/principal")
        try:
            self.service.excluir_artigo(artigo_id)
            flash("Artigo removido com sucesso.", "success")
        except Exception as e:
            flash(str(e), "error")
        return redirect("/admin?tab=artigos")

    # O ADM cadastra um artigo já APROVADO (o Service usa revisado='1').
    def cadastrar_artigo(self):
        if not self._verificar_adm():
            return redirect("/principal")
        titulo = request.form.get("titulo")
        url = request.form.get("url")
        origem = request.form.get("origem")
        autor = request.form.get("autor")
        ano_artigo = request.form.get("ano_artigo")
        tipo = request.form.get("tipo")
        admin_email = session.get("usuario_email")

        try:
            self.service.cadastrar_artigo(
                titulo=titulo, url=url, origem=origem, autor=autor,
                ano_artigo=ano_artigo, tipo=tipo, admin_email=admin_email
            )
            flash("Novo artigo cadastrado e aprovado com sucesso!", "success")
        except Exception as e:
            flash(str(e), "error")
        return redirect("/admin?tab=artigos")

    # Exclui um feedback recebido (armazenado em feedbacks.json)
    def excluir_feedback(self, feedback_id):
        if not self._verificar_adm():
            return redirect("/principal")
        try:
            FeedbackService.excluir_feedback(feedback_id)
            flash("Feedback removido com sucesso.", "success")
        except Exception as e:
            flash(str(e), "error")
        return redirect("/admin?tab=feedbacks")
