# admin_dao.py — DAO DO PAINEL ADMINISTRATIVO
# Consultas de estatística e operações de moderação (limpar denúncias, ocultar, excluir).
from dao.conexao import Conexao

class AdminDAO:

    # Números do painel 'Visão Geral'. Usa COUNT(*) para contar linhas e
    # SUM(CASE WHEN ... THEN 1 ELSE 0 END) para contar só as que atendem a uma condição
    # (ex.: usuários ativos, posts ocultos, artigos pendentes). Devolve tudo num dicionário.
    def obter_estatisticas(self):
        con = Conexao.conectar()
        cur = con.cursor(dictionary=True)

        stats = {}

        # Usuários
        cur.execute("SELECT COUNT(*) AS total, SUM(CASE WHEN ativo='S' THEN 1 ELSE 0 END) AS ativos, SUM(CASE WHEN tipo='ADM' THEN 1 ELSE 0 END) AS adms FROM usuarios")
        stats["usuarios"] = cur.fetchone()

        # Fórum
        cur.execute("SELECT COUNT(*) AS total, SUM(CASE WHEN denuncia >= 3 THEN 1 ELSE 0 END) AS ocultos FROM forum")
        stats["forum_posts"] = cur.fetchone()

        cur.execute("SELECT COUNT(*) AS total, SUM(CASE WHEN ativo='N' THEN 1 ELSE 0 END) AS inativas FROM forum_respostas")
        stats["forum_respostas"] = cur.fetchone()

        # Relatos
        cur.execute("SELECT COUNT(*) AS total, SUM(CASE WHEN denuncia >= 3 THEN 1 ELSE 0 END) AS ocultos FROM relatos")
        stats["relatos"] = cur.fetchone()

        # Artigos
        cur.execute("""
            SELECT 
                COUNT(*) AS total,
                SUM(CASE WHEN revisado IN ('1', 'S') THEN 1 ELSE 0 END) AS aprovados,
                SUM(CASE WHEN revisado IN ('0', 'N') OR revisado IS NULL THEN 1 ELSE 0 END) AS pendentes,
                SUM(CASE WHEN revisado='R' THEN 1 ELSE 0 END) AS rejeitados
            FROM artigos
        """)
        stats["artigos"] = cur.fetchone()

        # Denúncias totais
        cur.execute("SELECT COUNT(*) AS total FROM forum_denuncia")
        stats["total_denuncias_forum"] = cur.fetchone()["total"]

        cur.execute("SELECT COUNT(*) AS total FROM forum_resposta_denuncia")
        stats["total_denuncias_respostas"] = cur.fetchone()["total"]

        cur.execute("SELECT COUNT(*) AS total FROM relato_denuncia")
        stats["total_denuncias_relatos"] = cur.fetchone()["total"]

        cur.close()
        con.close()
        return stats

    # Posts com alguma denúncia, os mais denunciados primeiro. Para cada post faz uma 2ª consulta
    # trazendo QUEM denunciou e quando (detalhes_denuncias), para o ADM ter contexto para decidir.
    def listar_posts_denunciados(self):
        con = Conexao.conectar()
        cur = con.cursor(dictionary=True)
        cur.execute("""
            SELECT f.id, f.autor_id, f.texto, f.criado_em, f.likes, f.denuncia,
                   COALESCE(u.nickname, u.nome) AS autor_nome,
                   COUNT(fd.id) AS total_denuncias
            FROM forum f
            JOIN usuarios u ON f.autor_id = u.email
            LEFT JOIN forum_denuncia fd ON f.id = fd.forum_id
            WHERE f.denuncia > 0 OR fd.id IS NOT NULL
            GROUP BY f.id, f.autor_id, f.texto, f.criado_em, f.likes, f.denuncia, autor_nome
            ORDER BY total_denuncias DESC, f.denuncia DESC
        """)
        posts = cur.fetchall()

        for p in posts:
            cur.execute("""
                SELECT fd.id, fd.usuario_email, fd.criado_em, COALESCE(u.nickname, u.nome) AS denunciante_nome
                FROM forum_denuncia fd
                LEFT JOIN usuarios u ON fd.usuario_email = u.email
                WHERE fd.forum_id = %s
                ORDER BY fd.criado_em DESC
            """, (p["id"],))
            p["detalhes_denuncias"] = cur.fetchall()

        cur.close()
        con.close()
        return posts

    # Apaga as denúncias do post e zera o contador: o post volta a ser visível.
    def limpar_denuncias_post(self, forum_id):
        con = Conexao.conectar()
        cur = con.cursor()
        cur.execute("DELETE FROM forum_denuncia WHERE forum_id = %s", (forum_id,))
        cur.execute("UPDATE forum SET denuncia = 0 WHERE id = %s", (forum_id,))
        con.commit()
        cur.close()
        con.close()

    # Ocultação manual: se já está oculto (>=3), zera; se não, força o valor 3 (que significa 'oculto').
    def alternar_ocultacao_post(self, forum_id):
        con = Conexao.conectar()
        cur = con.cursor(dictionary=True)
        cur.execute("SELECT denuncia FROM forum WHERE id = %s", (forum_id,))
        p = cur.fetchone()
        if p:
            novo_val = 0 if p["denuncia"] >= 3 else 3
            cur.execute("UPDATE forum SET denuncia = %s WHERE id = %s", (novo_val, forum_id))
            con.commit()
        cur.close()
        con.close()

    # Exclusão em CASCATA manual: precisa apagar primeiro os 'filhos' (denúncias, curtidas, respostas e as curtidas/denúncias
    # das respostas) para só depois apagar o post. Ordem importa por causa das chaves estrangeiras do banco.
    def excluir_post(self, forum_id):
        con = Conexao.conectar()
        cur = con.cursor()
        cur.execute("DELETE FROM forum_denuncia WHERE forum_id = %s", (forum_id,))
        cur.execute("DELETE FROM forum_curtidas WHERE forum_id = %s", (forum_id,))
        # Buscar respostas para limpar dependências
        cur.execute("SELECT id FROM forum_respostas WHERE forum_id = %s", (forum_id,))
        respostas = cur.fetchall()
        for r in respostas:
            cur.execute("DELETE FROM forum_resposta_denuncia WHERE resposta_id = %s", (r[0],))
            cur.execute("DELETE FROM forum_resposta_curtidas WHERE resposta_id = %s", (r[0],))
        cur.execute("DELETE FROM forum_respostas WHERE forum_id = %s", (forum_id,))
        cur.execute("DELETE FROM forum WHERE id = %s", (forum_id,))
        con.commit()
        cur.close()
        con.close()

    # Respostas com denúncia ou já inativas, com o texto do post original para contexto, e quem denunciou.
    def listar_respostas_denunciadas(self):
        con = Conexao.conectar()
        cur = con.cursor(dictionary=True)
        cur.execute("""
            SELECT r.id, r.forum_id, r.autor_email, r.texto, r.criado_em, r.likes, r.ativo,
                   COALESCE(u.nickname, u.nome) AS autor_nome, f.texto AS post_texto,
                   COUNT(frd.id) AS total_denuncias
            FROM forum_respostas r
            JOIN usuarios u ON r.autor_email = u.email
            JOIN forum f ON r.forum_id = f.id
            LEFT JOIN forum_resposta_denuncia frd ON r.id = frd.resposta_id
            WHERE r.ativo = 'N' OR frd.id IS NOT NULL
            GROUP BY r.id, r.forum_id, r.autor_email, r.texto, r.criado_em, r.likes, r.ativo, autor_nome, f.texto
            ORDER BY total_denuncias DESC, r.criado_em DESC
        """)
        respostas = cur.fetchall()

        for r in respostas:
            cur.execute("""
                SELECT frd.id, frd.usuario_email, COALESCE(u.nickname, u.nome) AS denunciante_nome
                FROM forum_resposta_denuncia frd
                LEFT JOIN usuarios u ON frd.usuario_email = u.email
                WHERE frd.resposta_id = %s
            """, (r["id"],))
            r["detalhes_denuncias"] = cur.fetchall()

        cur.close()
        con.close()
        return respostas

    # Inverte ativo S<->N da resposta.
    def alternar_status_resposta(self, resposta_id):
        con = Conexao.conectar()
        cur = con.cursor(dictionary=True)
        cur.execute("SELECT ativo FROM forum_respostas WHERE id = %s", (resposta_id,))
        r = cur.fetchone()
        if r:
            novo_ativo = 'N' if r["ativo"] == 'S' else 'S'
            cur.execute("UPDATE forum_respostas SET ativo = %s WHERE id = %s", (novo_ativo, resposta_id))
            con.commit()
        cur.close()
        con.close()

    # Apaga denúncias e reativa a resposta (ativo='S').
    def limpar_denuncias_resposta(self, resposta_id):
        con = Conexao.conectar()
        cur = con.cursor()
        cur.execute("DELETE FROM forum_resposta_denuncia WHERE resposta_id = %s", (resposta_id,))
        cur.execute("UPDATE forum_respostas SET ativo = 'S' WHERE id = %s", (resposta_id,))
        con.commit()
        cur.close()
        con.close()

    # Apaga as dependências (denúncias/curtidas) e depois a resposta.
    def excluir_resposta(self, resposta_id):
        con = Conexao.conectar()
        cur = con.cursor()
        cur.execute("DELETE FROM forum_resposta_denuncia WHERE resposta_id = %s", (resposta_id,))
        cur.execute("DELETE FROM forum_resposta_curtidas WHERE resposta_id = %s", (resposta_id,))
        cur.execute("DELETE FROM forum_respostas WHERE id = %s", (resposta_id,))
        con.commit()
        cur.close()
        con.close()

    # Relatos com denúncia, os mais denunciados primeiro, mais o detalhe de quem denunciou.
    def listar_relatos_denunciados(self):
        con = Conexao.conectar()
        cur = con.cursor(dictionary=True)
        cur.execute("""
            SELECT r.id, r.autor_email, r.texto, r.criado_em, r.likes, r.denuncia,
                   COALESCE(u.nickname, u.nome, r.autor_email) AS autor_nome,
                   COUNT(rd.id) AS total_denuncias
            FROM relatos r
            LEFT JOIN usuarios u ON r.autor_email = u.email
            LEFT JOIN relato_denuncia rd ON r.id = rd.relato_id
            WHERE r.denuncia > 0 OR rd.id IS NOT NULL
            GROUP BY r.id, r.autor_email, r.texto, r.criado_em, r.likes, r.denuncia, autor_nome
            ORDER BY total_denuncias DESC, r.denuncia DESC
        """)
        relatos = cur.fetchall()

        for rel in relatos:
            cur.execute("""
                SELECT rd.id, rd.usuario_email, rd.criado_em, COALESCE(u.nickname, u.nome) AS denunciante_nome
                FROM relato_denuncia rd
                LEFT JOIN usuarios u ON rd.usuario_email = u.email
                WHERE rd.relato_id = %s
                ORDER BY rd.criado_em DESC
            """, (rel["id"],))
            rel["detalhes_denuncias"] = cur.fetchall()

        cur.close()
        con.close()
        return relatos

    # Apaga denúncias e zera o contador do relato.
    def limpar_denuncias_relato(self, relato_id):
        con = Conexao.conectar()
        cur = con.cursor()
        cur.execute("DELETE FROM relato_denuncia WHERE relato_id = %s", (relato_id,))
        cur.execute("UPDATE relatos SET denuncia = 0 WHERE id = %s", (relato_id,))
        con.commit()
        cur.close()
        con.close()

    # Oculta/mostra relato manualmente (mesma ideia do valor 3).
    def alternar_ocultacao_relato(self, relato_id):
        con = Conexao.conectar()
        cur = con.cursor(dictionary=True)
        cur.execute("SELECT denuncia FROM relatos WHERE id = %s", (relato_id,))
        r = cur.fetchone()
        if r:
            novo_val = 0 if r["denuncia"] >= 3 else 3
            cur.execute("UPDATE relatos SET denuncia = %s WHERE id = %s", (novo_val, relato_id))
            con.commit()
        cur.close()
        con.close()

    # Apaga denúncias, curtidas e o relato.
    def excluir_relato(self, relato_id):
        con = Conexao.conectar()
        cur = con.cursor()
        cur.execute("DELETE FROM relato_denuncia WHERE relato_id = %s", (relato_id,))
        cur.execute("DELETE FROM relato_curtidas WHERE relato_id = %s", (relato_id,))
        cur.execute("DELETE FROM relatos WHERE id = %s", (relato_id,))
        con.commit()
        cur.close()
        con.close()

    # Troca ADM <-> Portador. Levanta erro se o usuário não existe. Devolve o novo tipo para a mensagem na tela.
    def alternar_tipo_usuario(self, email):
        con = Conexao.conectar()
        cur = con.cursor(dictionary=True)
        cur.execute("SELECT tipo FROM usuarios WHERE email = %s", (email,))
        u = cur.fetchone()
        if not u:
            cur.close()
            con.close()
            raise Exception("Usuário não encontrado.")

        novo_tipo = 'Portador' if u["tipo"] == 'ADM' else 'ADM'
        cur.execute("UPDATE usuarios SET tipo = %s WHERE email = %s", (novo_tipo, email))
        con.commit()
        cur.close()
        con.close()
        return novo_tipo
