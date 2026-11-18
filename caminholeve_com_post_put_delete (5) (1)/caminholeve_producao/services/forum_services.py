# forum_services.py — SERVICE DO FÓRUM
# Valida os dados (texto vazio, usuário logado) antes de chamar o DAO. Também 'junta' cada post com suas respostas.
from dao.forum_dao import ForumDAO
from models.forum_model import Forum, ForumResposta

class ForumService:
    def __init__(self):
        self.dao = ForumDAO()

    # Busca os posts e, para CADA post, busca as respostas e anexa no objeto (post.set_respostas).
    # Assim o template recebe uma estrutura pronta: post -> lista de respostas.
    def listar_forum(self, usuario_email=None):
        posts = self.dao.listar_posts(usuario_email)
        for post in posts:
            respostas = self.dao.listar_respostas_por_post(post.get_id(), usuario_email)
            post.set_respostas(respostas)
        return posts

    # Regras: texto não pode ser vazio e precisa ter autor. .strip() remove espaços sobrando.
    def criar_post(self, autor_id, texto):
        if not texto or not texto.strip():
            raise Exception("O texto do post não pode estar vazio.")
        if not autor_id:
            raise Exception("Usuário precisa estar logado para publicar.")
            
        post = Forum(autor_id=autor_id, texto=texto.strip())
        self.dao.inserir_post(post)
        return post

    # Regras: precisa de id do post, texto e autor. int(forum_id) converte o texto do formulário em número.
    def criar_resposta(self, forum_id, autor_email, texto):
        if not forum_id:
            raise Exception("ID do fórum não fornecido.")
        if not texto or not texto.strip():
            raise Exception("O texto da resposta não pode estar vazio.")
        if not autor_email:
            raise Exception("Usuário precisa estar logado para responder.")
            
        resposta = ForumResposta(forum_id=int(forum_id), autor_email=autor_email, texto=texto.strip())
        self.dao.inserir_resposta(resposta)
        return resposta

    # Liga/desliga a curtida do usuário naquele post.
    def curtir_post(self, forum_id, usuario_email):
        if not forum_id:
            raise Exception("ID do fórum não fornecido.")
        if not usuario_email:
            raise Exception("Usuário precisa estar logado para curtir.")
        return self.dao.alternar_curtida_post(int(forum_id), usuario_email)

    # Liga/desliga a curtida em uma resposta.
    def curtir_resposta(self, resposta_id, usuario_email):
        if not resposta_id:
            raise Exception("ID da resposta não fornecido.")
        if not usuario_email:
            raise Exception("Usuário precisa estar logado para curtir.")
        return self.dao.alternar_curtida_resposta(int(resposta_id), usuario_email)

    # Delega ao DAO, que conta as denúncias e inativa a resposta no 3º aviso.
    def denunciar_resposta(self, resposta_id, usuario_email):
        if not resposta_id:
            raise Exception("ID da resposta não fornecido.")
        if not usuario_email:
            raise Exception("Usuário precisa estar logado para denunciar.")
        return self.dao.denunciar_resposta(int(resposta_id), usuario_email)

    # Delega ao DAO, que conta as denúncias e oculta o post no 3º aviso.
    def denunciar_post(self, forum_id, usuario_email):
        if not forum_id:
            raise Exception("ID da publicação não fornecido.")
        if not usuario_email:
            raise Exception("Usuário precisa estar logado para denunciar.")
        return self.dao.denunciar_post(int(forum_id), usuario_email)
