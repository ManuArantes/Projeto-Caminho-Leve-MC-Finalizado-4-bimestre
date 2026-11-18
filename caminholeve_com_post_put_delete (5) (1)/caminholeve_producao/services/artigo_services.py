# artigo_services.py — SERVICE DOS ARTIGOS
# Regras: título e URL obrigatórios. Controla o ciclo de moderação: pendente ('0') -> aprovado ('1') ou rejeitado ('R').

from dao.artigo_dao import ArtigoDAO
from models.artigo_model import Artigo

class ArtigoService:
    def __init__(self):
        self.dao = ArtigoDAO()

    # Só os artigos APROVADOS (os que aparecem para o público).
    def listar(self):
        return self.dao.listar_aprovados()

    # Lista os artigos aprovados com paginação (padrão: 3 artigos por página).
    def listar_paginado(self, pagina=1, por_pagina=3):
        import math
        total = self.dao.contar_aprovados()
        total_paginas = max(1, math.ceil(total / por_pagina))

        if pagina < 1:
            pagina = 1
        elif pagina > total_paginas:
            pagina = total_paginas

        offset = (pagina - 1) * por_pagina
        artigos = self.dao.listar_aprovados_paginado(limite=por_pagina, offset=offset)
        return artigos, total, total_paginas, pagina

    # Todos, de qualquer status (uso do ADM).
    def listar_todos(self):
        return self.dao.listar()

    # Sugestões feitas por um usuário específico.
    def listar_por_usuario(self, email):
        return self.dao.listar_por_usuario(email)

    def buscar(self, id):
        return self.dao.buscar(id)

    # Valida título/URL, limpa espaços e grava. 'revisado' define o status inicial ('0' sugestão de usuário, '1' cadastro feito pelo ADM).
    def cadastrar(self, titulo, url, origem, autor, revisado="0", criado_por=None, ano_artigo=None, tipo=None):
        if not titulo or not titulo.strip():
            raise Exception("O título do artigo é obrigatório.")
        if not url or not url.strip():
            raise Exception("A URL do artigo é obrigatória.")

        artigo = Artigo(
            titulo=titulo.strip(), url=url.strip(), origem=origem.strip() if origem else None,
            autor=autor.strip() if autor else None, revisado=revisado, criado_por=criado_por,
            ano_artigo=ano_artigo.strip() if ano_artigo else None, tipo=tipo.strip() if tipo else None
        )
        self.dao.inserir(artigo)
        return artigo

    # Muda status para '1' e registra quem aprovou.
    def aprovar(self, id, aprovado_por):
        self.dao.atualizar_status(id, "1", aprovado_por)

    # Muda status para 'R'.
    def rejeitar(self, id, aprovado_por=None):
        self.dao.atualizar_status(id, "R", aprovado_por)

    # Remove o artigo.
    def excluir(self, id):
        self.dao.excluir(id)

    # Atualiza os dados de um artigo existente (PUT).
    def atualizar(self, id, titulo, url, origem=None, autor=None, ano_artigo=None, tipo=None):
        artigo_existente = self.dao.buscar(id)
        if not artigo_existente:
            raise Exception("Artigo não encontrado.")
        if not titulo or not titulo.strip():
            raise Exception("O título do artigo é obrigatório.")
        if not url or not url.strip():
            raise Exception("A URL do artigo é obrigatória.")

        artigo = Artigo(
            id=id, titulo=titulo.strip(), url=url.strip(),
            origem=origem.strip() if isinstance(origem, str) and origem.strip() else None,
            autor=autor.strip() if isinstance(autor, str) and autor.strip() else None,
            ano_artigo=ano_artigo.strip() if isinstance(ano_artigo, str) and ano_artigo.strip() else None,
            tipo=tipo.strip() if isinstance(tipo, str) and tipo.strip() else None
        )
        if not self.dao.atualizar(id, artigo):
            raise Exception("Nenhuma alteração foi realizada.")
        return self.dao.buscar(id)
