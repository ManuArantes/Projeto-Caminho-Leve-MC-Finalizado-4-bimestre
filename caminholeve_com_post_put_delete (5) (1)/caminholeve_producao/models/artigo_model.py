# artigo_model.py — MODEL do ARTIGO MÉDICO
# Representa uma linha da tabela `artigos`.

class Artigo:
    # revisado -> status de moderação:  '0' = pendente  |  '1' = aprovado  |  'R' = rejeitado
    # criado_por -> e-mail de quem sugeriu o artigo
    # origem -> revista/fonte (ex.: 'Revista Paulista de Pediatria')
    # tipo -> 'Relato de Caso', 'Artigo Científico' etc.
    def __init__(self, id=None, titulo=None, url=None, origem=None,
                 autor=None, revisado=None, criado_por=None, criado_em=None,
                 ano_artigo=None, tipo=None):
        self.__id = id
        self.__titulo = titulo
        self.__url = url
        self.__origem = origem
        self.__autor = autor
        self.__revisado = revisado
        self.__criado_por = criado_por
        self.__criado_em = criado_em
        self.__ano_artigo = ano_artigo
        self.__tipo = tipo

    # Getters (leitura).
    def get_id(self): return self.__id
    def get_titulo(self): return self.__titulo
    def get_url(self): return self.__url
    def get_origem(self): return self.__origem
    def get_autor(self): return self.__autor
    def get_revisado(self): return self.__revisado
    def get_criado_por(self): return self.__criado_por
    def get_criado_em(self): return self.__criado_em
    def get_ano_artigo(self): return self.__ano_artigo
    def get_tipo(self): return self.__tipo

    # Setters (escrita).
    def set_id(self, v): self.__id = v
    def set_titulo(self, v): self.__titulo = v
    def set_url(self, v): self.__url = v
    def set_origem(self, v): self.__origem = v
    def set_autor(self, v): self.__autor = v
    def set_revisado(self, v): self.__revisado = v
    def set_criado_por(self, v): self.__criado_por = v
    def set_criado_em(self, v): self.__criado_em = v
    def set_ano_artigo(self, v): self.__ano_artigo = v
    def set_tipo(self, v): self.__tipo = v

    # Converte o objeto Artigo em dicionário (para retornar em JSON na API / React)
    def to_dict(self):
        return {
            "id": self.__id,
            "titulo": self.__titulo,
            "url": self.__url,
            "origem": self.__origem,
            "autor": self.__autor,
            "ano_artigo": self.__ano_artigo,
            "tipo": self.__tipo,
            "revisado": self.__revisado,
            "criado_por": self.__criado_por,
            "criado_em": self.__criado_em.isoformat() if hasattr(self.__criado_em, "isoformat") else str(self.__criado_em or ""),
        }

