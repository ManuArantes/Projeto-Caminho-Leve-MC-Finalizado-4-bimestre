# relato_dao.py — DAO DOS RELATOS
# Tabelas: relatos, relato_curtidas, relato_denuncia. A lógica é igual à do fórum
# (curtir liga/desliga, denúncia única por usuário, oculto com 3+ denúncias).
from dao.conexao import Conexao
from models.relato_model import Relato

class RelatoDAO:

    # Lista relatos, mais novos primeiro. LEFT JOIN + COALESCE: mostra o apelido; sem apelido, o nome;
    # se o autor não existir na tabela usuarios, mostra o e-mail em vez de sumir com o relato.
    # Relatos com 3+ denúncias ficam ocultos (exceto para o próprio autor).
    def listar_relatos(self, usuario_email=None):
        con = Conexao.conectar()
        cur = con.cursor(dictionary=True)
        # Se um relato tiver 3 ou mais denúncias, não deve aparecer para os demais usuários
        if usuario_email:
            cur.execute(
                "SELECT r.*, COALESCE(u.nickname, u.nome, r.autor_email) AS autor_nome FROM relatos r "
                "LEFT JOIN usuarios u ON r.autor_email = u.email "
                "WHERE (COALESCE(r.denuncia, 0) < 3 OR r.autor_email = %s) "
                "ORDER BY r.criado_em DESC",
                (usuario_email,)
            )
        else:
            cur.execute(
                "SELECT r.*, COALESCE(u.nickname, u.nome, r.autor_email) AS autor_nome FROM relatos r "
                "LEFT JOIN usuarios u ON r.autor_email = u.email "
                "WHERE COALESCE(r.denuncia, 0) < 3 "
                "ORDER BY r.criado_em DESC"
            )
        dados = cur.fetchall()

        lista = []
        for d in dados:
            relato = Relato(
                id=d["id"],
                autor_email=d["autor_email"],
                autor_nome=d["autor_nome"],
                texto=d["texto"],
                criado_em=d["criado_em"],
                likes=d["likes"] if d["likes"] is not None else 0,
                denuncia=d.get("denuncia", 0) if d.get("denuncia") is not None else 0
            )

            # Verificar se o usuário atual curtiu
            if usuario_email:
                cur.execute(
                    "SELECT 1 FROM relato_curtidas WHERE relato_id = %s AND usuario_email = %s",
                    (relato.get_id(), usuario_email)
                )
                if cur.fetchone():
                    relato.set_curtido_pelo_usuario(True)

            lista.append(relato)

        cur.close()
        con.close()
        return lista

    # INSERT do relato (likes e denuncia começam em 0).
    def inserir_relato(self, relato):
        con = Conexao.conectar()
        cur = con.cursor()
        cur.execute(
            "INSERT INTO relatos (autor_email, texto, criado_em, likes, denuncia) "
            "VALUES (%s, %s, NOW(), 0, 0)",
            (relato.get_autor_email(), relato.get_texto())
        )
        con.commit()
        relato.set_id(cur.lastrowid)
        cur.close()
        con.close()

    # Curtir/descurtir (liga/desliga) e ajusta o contador likes.
    def alternar_curtida(self, relato_id, usuario_email):
        con = Conexao.conectar()
        cur = con.cursor()
        cur.execute(
            "SELECT id FROM relato_curtidas WHERE relato_id = %s AND usuario_email = %s",
            (relato_id, usuario_email)
        )
        registro = cur.fetchone()

        if registro:
            cur.execute(
                "DELETE FROM relato_curtidas WHERE relato_id = %s AND usuario_email = %s",
                (relato_id, usuario_email)
            )
            cur.execute(
                "UPDATE relatos SET likes = GREATEST(likes - 1, 0) WHERE id = %s",
                (relato_id,)
            )
            curtida_adicionada = False
        else:
            cur.execute(
                "INSERT INTO relato_curtidas (relato_id, usuario_email) VALUES (%s, %s)",
                (relato_id, usuario_email)
            )
            cur.execute(
                "UPDATE relatos SET likes = likes + 1 WHERE id = %s",
                (relato_id,)
            )
            curtida_adicionada = True

        con.commit()
        cur.close()
        con.close()
        return curtida_adicionada

    # Registra denúncia: não pode ser do próprio autor, nem repetida. O total vai para relatos.denuncia.
    def denunciar_relato(self, relato_id, usuario_email):
        con = Conexao.conectar()
        cur = con.cursor()

        # Obter dados do relato
        cur.execute(
            "SELECT autor_email FROM relatos WHERE id = %s",
            (relato_id,)
        )
        relato_data = cur.fetchone()
        if not relato_data:
            cur.close()
            con.close()
            raise Exception("Relato não encontrado.")

        autor_email = relato_data[0]
        if autor_email == usuario_email:
            cur.close()
            con.close()
            raise Exception("Você não pode denunciar seu próprio relato.")

        # Verificar se já denunciou
        cur.execute(
            "SELECT id FROM relato_denuncia WHERE relato_id = %s AND usuario_email = %s",
            (relato_id, usuario_email)
        )
        registro = cur.fetchone()

        if not registro:
            # Inserir denúncia na tabela relato_denuncia
            cur.execute(
                "INSERT INTO relato_denuncia (relato_id, usuario_email) VALUES (%s, %s)",
                (relato_id, usuario_email)
            )

            # Contar denúncias deste relato
            cur.execute(
                "SELECT COUNT(*) FROM relato_denuncia WHERE relato_id = %s",
                (relato_id,)
            )
            total_denuncias = cur.fetchone()[0]

            # Atualizar coluna denuncia na tabela relatos
            cur.execute(
                "UPDATE relatos SET denuncia = %s WHERE id = %s",
                (total_denuncias, relato_id)
            )
            con.commit()
            ocultado = total_denuncias >= 3
        else:
            cur.close()
            con.close()
            raise Exception("Você já denunciou este relato.")

        cur.close()
        con.close()
        return ocultado
