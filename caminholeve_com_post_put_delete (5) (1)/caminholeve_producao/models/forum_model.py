# Uma mensagem (post) do fórum — tabela `forum`.
# forum_model.py — MODELS do FÓRUM
# Este arquivo tem DUAS classes: Forum (a mensagem principal) e ForumResposta (resposta a uma mensagem).
class Forum:
    # autor_id   -> e-mail do autor
    # autor_nome -> vem do JOIN com usuarios (só para exibir)
    # respostas  -> lista de objetos ForumResposta (preenchida pelo Service)
    # denuncia   -> total de denúncias (>= 3 esconde o post)
    def __init__(self, id=None, autor_id=None, autor_nome=None, texto=None, criado_em=None, likes=0, respostas=None, denuncia=0):
        self.__id = id
        self.__autor_id = autor_id
        self.__autor_nome = autor_nome
        self.__texto = texto
        self.__criado_em = criado_em
        self.__likes = likes
        self.__respostas = respostas if respostas is not None else []
        self.__denuncia = denuncia if denuncia is not None else 0
        self.__curtido_pelo_usuario = False

    # Getters (leitura).
    def get_id(self): return self.__id
    def get_autor_id(self): return self.__autor_id
    def get_autor_nome(self): return self.__autor_nome
    def get_texto(self): return self.__texto
    def get_criado_em(self): return self.__criado_em
    def get_likes(self): return self.__likes
    def get_respostas(self): return self.__respostas
    def get_denuncia(self): return self.__denuncia
    def get_curtido_pelo_usuario(self): return self.__curtido_pelo_usuario

    # Setters (escrita).
    def set_id(self, v): self.__id = v
    def set_autor_id(self, v): self.__autor_id = v
    def set_autor_nome(self, v): self.__autor_nome = v
    def set_texto(self, v): self.__texto = v
    def set_criado_em(self, v): self.__criado_em = v
    def set_likes(self, v): self.__likes = v
    def set_respostas(self, v): self.__respostas = v
    def set_denuncia(self, v): self.__denuncia = v
    def set_curtido_pelo_usuario(self, v): self.__curtido_pelo_usuario = v


# Uma resposta dentro de um post — tabela `forum_respostas`.
class ForumResposta:
    # forum_id -> a qual post esta resposta pertence
    # ativo    -> 'S' visível | 'N' oculta (3 denúncias ou ação do ADM)
    def __init__(self, id=None, forum_id=None, autor_email=None, autor_nome=None, texto=None, criado_em=None, likes=0, ativo='S'):
        self.__id = id
        self.__forum_id = forum_id
        self.__autor_email = autor_email
        self.__autor_nome = autor_nome
        self.__texto = texto
        self.__criado_em = criado_em
        self.__likes = likes
        self.__ativo = ativo
        self.__curtido_pelo_usuario = False

    def get_id(self): return self.__id
    def get_forum_id(self): return self.__forum_id
    def get_autor_email(self): return self.__autor_email
    def get_autor_nome(self): return self.__autor_nome
    def get_texto(self): return self.__texto
    def get_criado_em(self): return self.__criado_em
    def get_likes(self): return self.__likes
    def get_ativo(self): return self.__ativo
    def get_curtido_pelo_usuario(self): return self.__curtido_pelo_usuario

    def set_id(self, v): self.__id = v
    def set_forum_id(self, v): self.__forum_id = v
    def set_autor_email(self, v): self.__autor_email = v
    def set_autor_nome(self, v): self.__autor_nome = v
    def set_texto(self, v): self.__texto = v
    def set_criado_em(self, v): self.__criado_em = v
    def set_likes(self, v): self.__likes = v
    def set_ativo(self, v): self.__ativo = v
    def set_curtido_pelo_usuario(self, v): self.__curtido_pelo_usuario = v
