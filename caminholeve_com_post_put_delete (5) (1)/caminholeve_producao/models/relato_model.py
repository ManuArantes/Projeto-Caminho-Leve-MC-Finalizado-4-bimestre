# relato_model.py — MODEL do RELATO
# Representa uma linha da tabela `relatos` (história pessoal compartilhada na aba 'Relatos').
class Relato:
    # autor_email -> e-mail de quem escreveu (chave estrangeira para usuarios)
    # autor_nome  -> NÃO existe na tabela relatos; vem do JOIN com usuarios, só para exibir o nome na tela
    # likes       -> total de curtidas ('pessoas se identificaram')
    # denuncia    -> total de denúncias (>= 3 oculta o relato)
    def __init__(self, id=None, autor_email=None, autor_nome=None, texto=None, criado_em=None, likes=0, denuncia=0):
        self.__id = id
        self.__autor_email = autor_email
        self.__autor_nome = autor_nome
        self.__texto = texto
        self.__criado_em = criado_em
        self.__likes = likes
        self.__denuncia = denuncia if denuncia is not None else 0
        self.__curtido_pelo_usuario = False

    # Getters (leitura).
    def get_id(self): return self.__id
    def get_autor_email(self): return self.__autor_email
    def get_autor_nome(self): return self.__autor_nome
    def get_texto(self): return self.__texto
    def get_criado_em(self): return self.__criado_em
    def get_likes(self): return self.__likes
    def get_denuncia(self): return self.__denuncia
    def get_curtido_pelo_usuario(self): return self.__curtido_pelo_usuario

    # Setters (escrita).
    def set_id(self, v): self.__id = v
    def set_autor_email(self, v): self.__autor_email = v
    def set_autor_nome(self, v): self.__autor_nome = v
    def set_texto(self, v): self.__texto = v
    def set_criado_em(self, v): self.__criado_em = v
    def set_likes(self, v): self.__likes = v
    def set_denuncia(self, v): self.__denuncia = v
    def set_curtido_pelo_usuario(self, v): self.__curtido_pelo_usuario = v
