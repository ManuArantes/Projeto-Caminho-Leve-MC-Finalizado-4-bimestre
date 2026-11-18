# relato_services.py — SERVICE DOS RELATOS
# Mesmas ideias do fórum, para os relatos pessoais.
from dao.relato_dao import RelatoDAO
from models.relato_model import Relato

class RelatoService:
    def __init__(self):
        self.dao = RelatoDAO()

    # Devolve os relatos visíveis (os com 3+ denúncias só aparecem para o próprio autor).
    def listar_relatos(self, usuario_email=None):
        return self.dao.listar_relatos(usuario_email)

    # Valida texto e autor; cria o objeto Relato e manda o DAO gravar.
    def criar_relato(self, autor_email, texto):
        if not texto or not texto.strip():
            raise Exception("O texto do relato não pode estar vazio.")
        if not autor_email:
            raise Exception("Usuário precisa estar logado para publicar.")

        relato = Relato(autor_email=autor_email, texto=texto.strip())
        self.dao.inserir_relato(relato)
        return relato

    # Liga/desliga a curtida.
    def curtir_relato(self, relato_id, usuario_email):
        if not relato_id:
            raise Exception("ID do relato não fornecido.")
        if not usuario_email:
            raise Exception("Usuário precisa estar logado para curtir.")
        return self.dao.alternar_curtida(int(relato_id), usuario_email)

    # Registra a denúncia (o DAO impede denunciar o próprio relato ou denunciar duas vezes).
    def denunciar_relato(self, relato_id, usuario_email):
        if not relato_id:
            raise Exception("ID do relato não fornecido.")
        if not usuario_email:
            raise Exception("Usuário precisa estar logado para denunciar.")
        return self.dao.denunciar_relato(int(relato_id), usuario_email)
