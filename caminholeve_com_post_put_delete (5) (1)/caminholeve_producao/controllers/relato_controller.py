# relato_controller.py — CONTROLLER DOS RELATOS
# Publicar, curtir e denunciar relatos (histórias pessoais). Mesma estrutura do ForumController,
# mas redireciona para a aba de relatos (?tab=relatos). A listagem fica no ForumController porque
# as duas abas estão na mesma página.
from flask import request, redirect, flash, session
from services.relato_services import RelatoService

class RelatoController:
    def __init__(self):
        self.service = RelatoService()

    # Publica um relato. Exige login.
    def criar_relato(self):
        usuario_email = session.get("usuario_email")
        if not usuario_email:
            flash("Você precisa estar logado para compartilhar seu relato.", "error")
            return redirect("/cadastro")

        texto = request.form.get("texto")
        try:
            self.service.criar_relato(usuario_email, texto)
            flash("Relato compartilhado com sucesso!", "success")
        except Exception as e:
            flash(str(e), "error")

        return redirect("/acolhimento?tab=relatos")

    # Curtir/descurtir relato ('pessoas se identificaram').
    def curtir_relato(self, relato_id):
        usuario_email = session.get("usuario_email")
        if not usuario_email:
            flash("Você precisa estar logado para interagir.", "error")
            return redirect("/cadastro")

        try:
            self.service.curtir_relato(relato_id, usuario_email)
        except Exception as e:
            flash(str(e), "error")

        return redirect("/acolhimento?tab=relatos")

    # Denuncia relato; True = ocultado após 3 denúncias.
    def denunciar_relato(self, relato_id):
        usuario_email = session.get("usuario_email")
        if not usuario_email:
            flash("Você precisa estar logado para denunciar.", "error")
            return redirect("/cadastro")

        try:
            ocultado = self.service.denunciar_relato(relato_id, usuario_email)
            if ocultado:
                flash("Relato ocultado após receber 3 denúncias.", "success")
            else:
                flash("Relato denunciado com sucesso.", "success")
        except Exception as e:
            flash(str(e), "error")

        return redirect("/acolhimento?tab=relatos")
