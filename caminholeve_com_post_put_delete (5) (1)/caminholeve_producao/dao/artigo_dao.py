# artigo_dao.py — DAO DOS ARTIGOS MÉDICOS
# Tabela `artigos`. Coluna revisado: '0' pendente | '1' aprovado | 'R' rejeitado.

from dao.conexao import Conexao
from models.artigo_model import Artigo

class ArtigoDAO:

    # TODOS os artigos, de qualquer status (painel ADM). SELECT * traz todas as colunas.
    def listar(self):
        con = Conexao.conectar()
        cur = con.cursor(dictionary=True)
        cur.execute("SELECT * FROM artigos ORDER BY criado_em DESC")
        dados = cur.fetchall()
        cur.close()
        con.close()

        lista = []
        for d in dados:
            lista.append(Artigo(
                id=d["id"], titulo=d["titulo"], url=d["url"], origem=d["origem"],
                autor=d["autor"], revisado=d["revisado"], criado_por=d["criado_por"],
                criado_em=d["criado_em"], ano_artigo=d.get("ano_artigo"), tipo=d.get("tipo")
            ))
        return lista

    # Um artigo pelo id (ou None).
    def buscar(self, id):
        con = Conexao.conectar()
        cur = con.cursor(dictionary=True)
        cur.execute("SELECT * FROM artigos WHERE id=%s", (id,))
        d = cur.fetchone()
        cur.close()
        con.close()
        if d:
            return Artigo(
                id=d["id"], titulo=d["titulo"], url=d["url"], origem=d["origem"],
                autor=d["autor"], revisado=d["revisado"], criado_por=d["criado_por"],
                criado_em=d["criado_em"], ano_artigo=d.get("ano_artigo"), tipo=d.get("tipo")
            )
        return None

    # Somente aprovados (revisado = '1' ou 'S'): é a lista pública da página /artigos.
    def listar_aprovados(self):
        con = Conexao.conectar()
        cur = con.cursor(dictionary=True)
        cur.execute("SELECT * FROM artigos WHERE revisado IN ('1', 'S') ORDER BY criado_em DESC")
        dados = cur.fetchall()
        cur.close()
        con.close()

        lista = []
        for d in dados:
            lista.append(Artigo(
                id=d["id"], titulo=d["titulo"], url=d["url"], origem=d["origem"],
                autor=d["autor"], revisado=d["revisado"], criado_por=d["criado_por"],
                criado_em=d["criado_em"], ano_artigo=d.get("ano_artigo"), tipo=d.get("tipo")
            ))
        return lista

    # Conta o total de artigos aprovados no banco (para calcular o número de páginas).
    def contar_aprovados(self):
        con = Conexao.conectar()
        cur = con.cursor(dictionary=True)
        cur.execute("SELECT COUNT(*) AS total FROM artigos WHERE revisado IN ('1', 'S')")
        linha = cur.fetchone()
        cur.close()
        con.close()
        return linha["total"] if linha else 0

    # Busca apenas os artigos aprovados da página atual usando LIMIT e OFFSET no MySQL.
    def listar_aprovados_paginado(self, limite=3, offset=0):
        con = Conexao.conectar()
        cur = con.cursor(dictionary=True)
        cur.execute(
            "SELECT * FROM artigos WHERE revisado IN ('1', 'S') ORDER BY criado_em DESC LIMIT %s OFFSET %s",
            (int(limite), int(offset))
        )
        dados = cur.fetchall()
        cur.close()
        con.close()

        lista = []
        for d in dados:
            lista.append(Artigo(
                id=d["id"], titulo=d["titulo"], url=d["url"], origem=d["origem"],
                autor=d["autor"], revisado=d["revisado"], criado_por=d["criado_por"],
                criado_em=d["criado_em"], ano_artigo=d.get("ano_artigo"), tipo=d.get("tipo")
            ))
        return lista

    # Artigos sugeridos por um e-mail, com qualquer status (seção 'Minhas sugestões').
    def listar_por_usuario(self, email):
        con = Conexao.conectar()
        cur = con.cursor(dictionary=True)
        cur.execute("SELECT * FROM artigos WHERE criado_por = %s ORDER BY criado_em DESC", (email,))
        dados = cur.fetchall()
        cur.close()
        con.close()

        lista = []
        for d in dados:
            lista.append(Artigo(
                id=d["id"], titulo=d["titulo"], url=d["url"], origem=d["origem"],
                autor=d["autor"], revisado=d["revisado"], criado_por=d["criado_por"],
                criado_em=d["criado_em"], ano_artigo=d.get("ano_artigo"), tipo=d.get("tipo")
            ))
        return lista

    # Aprova/rejeita: muda 'revisado' e registra em 'aprovado_por' o e-mail do ADM que decidiu.
    def atualizar_status(self, id, revisado, aprovado_por=None):
        con = Conexao.conectar()
        cur = con.cursor()
        cur.execute(
            "UPDATE artigos SET revisado = %s, aprovado_por = %s WHERE id = %s",
            (revisado, aprovado_por, id)
        )
        con.commit()
        cur.close()
        con.close()

    # DELETE do artigo.
    def excluir(self, id):
        con = Conexao.conectar()
        cur = con.cursor()
        cur.execute("DELETE FROM artigos WHERE id = %s", (id,))
        con.commit()
        cur.close()
        con.close()

    # INSERT de um novo artigo (pendente ou já aprovado, conforme o valor de revisado).
    def inserir(self, artigo):
        con = Conexao.conectar()
        cur = con.cursor()
        cur.execute(
            "INSERT INTO artigos (titulo, url, origem, autor, ano_artigo, tipo, revisado, criado_por, criado_em) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())",
            (artigo.get_titulo(), artigo.get_url(), artigo.get_origem(),
             artigo.get_autor(), artigo.get_ano_artigo(), artigo.get_tipo(),
             artigo.get_revisado(), artigo.get_criado_por())
        )
        con.commit()
        cur.close()
        con.close()

    # Atualiza os dados principais de um artigo (PUT da API REST).
    def atualizar(self, id, artigo):
        con = Conexao.conectar()
        cur = con.cursor()
        cur.execute(
            "UPDATE artigos SET titulo=%s, url=%s, origem=%s, autor=%s, ano_artigo=%s, tipo=%s WHERE id=%s",
            (artigo.get_titulo(), artigo.get_url(), artigo.get_origem(),
             artigo.get_autor(), artigo.get_ano_artigo(), artigo.get_tipo(), id)
        )
        con.commit()
        alterados = cur.rowcount
        cur.close()
        con.close()
        return alterados > 0
