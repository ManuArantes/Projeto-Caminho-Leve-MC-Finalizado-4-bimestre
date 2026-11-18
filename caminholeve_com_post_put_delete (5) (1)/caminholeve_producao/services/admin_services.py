# admin_services.py — SERVICE DO PAINEL ADMINISTRATIVO
# Quase tudo aqui é 'repasse': o AdminController pede, este Service delega ao DAO certo.
# Ele reúne vários DAOs (admin, usuário, artigo) para o painel ter tudo em um só lugar.
from dao.admin_dao import AdminDAO
from dao.usuario_dao import UsuarioDAO
from dao.artigo_dao import ArtigoDAO
from services.artigo_services import ArtigoService

class AdminService:
    # Cria os DAOs que serão usados.
    def __init__(self):
        self.admin_dao = AdminDAO()
        self.usuario_dao = UsuarioDAO()
        self.artigo_dao = ArtigoDAO()
        self.artigo_service = ArtigoService()

    # Monta o dicionário com TUDO que a tela admin.html precisa: estatísticas, usuários, itens denunciados e artigos.
    def obter_painel_dados(self):
        return {
            "estatisticas": self.admin_dao.obter_estatisticas(),
            "usuarios": self.usuario_dao.listar_todos(),
            "posts_denunciados": self.admin_dao.listar_posts_denunciados(),
            "respostas_denunciadas": self.admin_dao.listar_respostas_denunciadas(),
            "relatos_denunciados": self.admin_dao.listar_relatos_denunciados(),
            "artigos": self.artigo_dao.listar()
        }

    # ----- USUÁRIOS -----
    # Usuários
    def alternar_status_usuario(self, email):
        return self.usuario_dao.alternar_status(email)

    def alternar_tipo_usuario(self, email):
        return self.admin_dao.alternar_tipo_usuario(email)

    # ----- FÓRUM -----
    # Fórum
    def limpar_denuncias_post(self, forum_id):
        self.admin_dao.limpar_denuncias_post(forum_id)

    def alternar_ocultacao_post(self, forum_id):
        self.admin_dao.alternar_ocultacao_post(forum_id)

    def excluir_post(self, forum_id):
        self.admin_dao.excluir_post(forum_id)

    # ----- RESPOSTAS -----
    # Respostas
    def alternar_status_resposta(self, resposta_id):
        self.admin_dao.alternar_status_resposta(resposta_id)

    def limpar_denuncias_resposta(self, resposta_id):
        self.admin_dao.limpar_denuncias_resposta(resposta_id)

    def excluir_resposta(self, resposta_id):
        self.admin_dao.excluir_resposta(resposta_id)

    # ----- RELATOS -----
    # Relatos
    def limpar_denuncias_relato(self, relato_id):
        self.admin_dao.limpar_denuncias_relato(relato_id)

    def alternar_ocultacao_relato(self, relato_id):
        self.admin_dao.alternar_ocultacao_relato(relato_id)

    def excluir_relato(self, relato_id):
        self.admin_dao.excluir_relato(relato_id)

    # ----- ARTIGOS ----- (aproveita o ArtigoService para manter a regra em um lugar só)
    # Artigos
    def aprovar_artigo(self, artigo_id, admin_email):
        self.artigo_service.aprovar(artigo_id, admin_email)

    def rejeitar_artigo(self, artigo_id, admin_email):
        self.artigo_service.rejeitar(artigo_id, admin_email)

    def excluir_artigo(self, artigo_id):
        self.artigo_service.excluir(artigo_id)

    # Artigo cadastrado pelo ADM já entra APROVADO (revisado='1').
    def cadastrar_artigo(self, titulo, url, origem, autor, ano_artigo, tipo, admin_email):
        return self.artigo_service.cadastrar(
            titulo=titulo, url=url, origem=origem, autor=autor,
            revisado="1", criado_por=admin_email, ano_artigo=ano_artigo, tipo=tipo
        )
