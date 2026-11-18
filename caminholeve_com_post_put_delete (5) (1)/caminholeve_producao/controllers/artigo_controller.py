# artigo_controller.py — CONTROLLER DOS ARTIGOS MÉDICOS (parte pública)
# Lista os artigos aprovados e recebe sugestões de usuários logados.
# (Aprovar/rejeitar fica no AdminController.)

from flask import render_template, request, redirect, flash, session, jsonify
from services.artigo_services import ArtigoService
from services.jwt_service import JWTService

class ArtigoController:
    def __init__(self):
        self.service = ArtigoService()

    def _obter_email_jwt(self):
        token = JWTService.extrair_token_requisicao()
        payload = JWTService.decodificar_token(token)
        if payload:
            return payload.get("usuario_email")
        return None

    # Página /artigos. Envia ao template:
    #   artigos            -> lista dos APROVADOS da página atual (3 por página)
    #   total              -> quantidade total de aprovados, para o contador no topo
    #   pagina_atual       -> número da página atual
    #   total_paginas      -> total de páginas disponíveis
    #   minhas_sugestoes   -> sugestões do usuário logado via JWT (com status pendente/aprovado/rejeitado)
    def artigos(self):
        import math
        usuario_email = self._obter_email_jwt()
        pagina = request.args.get("page", 1, type=int)
        por_pagina = 3

        artigos = self.service.listar()
        total = len(artigos)
        total_paginas = max(1, math.ceil(total / por_pagina))
        pagina_atual = max(1, min(pagina, total_paginas))

        minhas_sugestoes = []
        if usuario_email:
            try:
                minhas_sugestoes = self.service.listar_por_usuario(usuario_email)
            except Exception:
                minhas_sugestoes = []

        return render_template(
            "artigos.html",
            artigos=artigos,
            total=total,
            pagina_atual=pagina_atual,
            total_paginas=total_paginas,
            por_pagina=por_pagina,
            minhas_sugestoes=minhas_sugestoes
        )

    # Recebe o formulário do modal 'Sugerir artigo'. Só usuário logado com JWT válido pode sugerir.
    def sugerir_artigo(self):
        usuario_email = self._obter_email_jwt()
        if not usuario_email:
            flash("Você precisa estar logado para sugerir um artigo médico.", "error")
            return redirect("/cadastro")

        titulo = request.form.get("titulo")
        url = request.form.get("url")
        origem = request.form.get("origem")
        autor = request.form.get("autor")
        ano_artigo = request.form.get("ano_artigo")
        tipo = request.form.get("tipo") or "Artigo Científico"

        try:
            self.service.cadastrar(
                titulo=titulo, url=url, origem=origem, autor=autor,
                revisado="0", criado_por=usuario_email, ano_artigo=ano_artigo, tipo=tipo
            )
            flash("Indicação de artigo enviada com sucesso! Ela será avaliada pelo administrador.", "success")
        except Exception as e:
            flash(str(e), "error")

        return redirect("/artigos")

    # API REST (JSON puro, sem Jinja) para consumo pelo front-end em React (GET /api/artigos)
    def listar_artigos_json(self):
        pagina = request.args.get("page", type=int)
        por_pagina = request.args.get("per_page", 3, type=int)

        if pagina is not None:
            artigos, total, total_paginas, pagina_atual = self.service.listar_paginado(
                pagina=pagina,
                por_pagina=por_pagina
            )
        else:
            artigos = self.service.listar()
            total = len(artigos)
            total_paginas = 1
            pagina_atual = 1

        resposta = jsonify({
            "sucesso": True,
            "total": total,
            "pagina_atual": pagina_atual,
            "total_paginas": total_paginas,
            "artigos": [a.to_dict() for a in artigos]
        })
        # Permite que o React (ex.: http://localhost:3000 ou 5173) consuma a rota via fetch/axios
        resposta.headers["Access-Control-Allow-Origin"] = "*"
        return resposta


    # POST /api/artigos: cria uma sugestão pendente para o usuário autenticado.
    def criar_artigo_json(self):
        usuario_email = self._obter_email_jwt()
        if not usuario_email:
            return jsonify({"sucesso": False, "mensagem": "Autenticação necessária."}), 401
        dados = request.get_json(silent=True) or {}
        try:
            artigo = self.service.cadastrar(
                titulo=dados.get("titulo"), url=dados.get("url"),
                origem=dados.get("origem"), autor=dados.get("autor"),
                revisado="0", criado_por=usuario_email,
                ano_artigo=dados.get("ano_artigo"), tipo=dados.get("tipo") or "Artigo Científico"
            )
            return jsonify({"sucesso": True, "mensagem": "Artigo enviado para avaliação.",
                            "artigo": artigo.to_dict()}), 201
        except Exception as e:
            return jsonify({"sucesso": False, "mensagem": str(e)}), 400

    # PUT /api/artigos/<id>: somente administradores podem editar artigos.
    def atualizar_artigo_json(self, artigo_id):
        payload = JWTService.decodificar_token(JWTService.extrair_token_requisicao())
        if not payload:
            return jsonify({"sucesso": False, "mensagem": "Autenticação necessária."}), 401
        if payload.get("usuario_tipo") != "ADM":
            return jsonify({"sucesso": False, "mensagem": "Apenas administradores podem editar artigos."}), 403
        dados = request.get_json(silent=True) or {}
        try:
            artigo = self.service.atualizar(
                id=artigo_id, titulo=dados.get("titulo"), url=dados.get("url"),
                origem=dados.get("origem"), autor=dados.get("autor"),
                ano_artigo=dados.get("ano_artigo"), tipo=dados.get("tipo")
            )
            return jsonify({"sucesso": True, "mensagem": "Artigo atualizado.",
                            "artigo": artigo.to_dict()}), 200
        except Exception as e:
            status = 404 if "não encontrado" in str(e).lower() else 400
            return jsonify({"sucesso": False, "mensagem": str(e)}), status

    # DELETE /api/artigos/<id>: somente administradores podem excluir artigos.
    def excluir_artigo_json(self, artigo_id):
        payload = JWTService.decodificar_token(JWTService.extrair_token_requisicao())
        if not payload:
            return jsonify({"sucesso": False, "mensagem": "Autenticação necessária."}), 401
        if payload.get("usuario_tipo") != "ADM":
            return jsonify({"sucesso": False, "mensagem": "Apenas administradores podem excluir artigos."}), 403
        try:
            if not self.service.buscar(artigo_id):
                return jsonify({"sucesso": False, "mensagem": "Artigo não encontrado."}), 404
            self.service.excluir(artigo_id)
            return jsonify({"sucesso": True, "mensagem": "Artigo excluído com sucesso."}), 200
        except Exception as e:
            return jsonify({"sucesso": False, "mensagem": str(e)}), 400
