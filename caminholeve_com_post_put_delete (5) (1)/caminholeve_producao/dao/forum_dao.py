# forum_dao.py — DAO DO FÓRUM
# Posts, respostas, curtidas e denúncias. Tabelas envolvidas:
#   forum, forum_respostas, forum_curtidas, forum_resposta_curtidas, forum_denuncia, forum_resposta_denuncia
# Tabelas de curtidas/denúncias têm um registro por (item, usuário): assim cada pessoa só curte/denuncia UMA vez.
from dao.conexao import Conexao
from models.forum_model import Forum, ForumResposta

class ForumDAO:

    # Lista os posts do mais novo para o mais antigo, já com o APELIDO do autor (JOIN com usuarios;
    # COALESCE usa o nome completo se a conta ainda não tiver apelido).
    # REGRA DE OCULTAÇÃO: post com 3 ou mais denúncias NÃO aparece para os outros;
    # o próprio autor continua vendo (por isso existe a versão da query com usuario_email).
    def listar_posts(self, usuario_email=None):
        con = Conexao.conectar()
        cur = con.cursor(dictionary=True)
        # Buscar posts ordenando por data de criacao decrescente
        # Se um post tiver 3 ou mais denuncias, nao aparece para os demais usuarios
        if usuario_email:
            cur.execute(
                "SELECT f.*, COALESCE(u.nickname, u.nome) AS autor_nome FROM forum f "
                "JOIN usuarios u ON f.autor_id = u.email "
                "WHERE (COALESCE(f.denuncia, 0) < 3 OR f.autor_id = %s) "
                "ORDER BY f.criado_em DESC",
                (usuario_email,)
            )
        else:
            cur.execute(
                "SELECT f.*, COALESCE(u.nickname, u.nome) AS autor_nome FROM forum f "
                "JOIN usuarios u ON f.autor_id = u.email "
                "WHERE COALESCE(f.denuncia, 0) < 3 "
                "ORDER BY f.criado_em DESC"
            )
        dados = cur.fetchall()
        
        lista = []
        for d in dados:
            post = Forum(
                id=d["id"],
                autor_id=d["autor_id"],
                autor_nome=d["autor_nome"],
                texto=d["texto"],
                criado_em=d["criado_em"],
                likes=d["likes"] if d["likes"] is not None else 0,
                denuncia=d.get("denuncia", 0) if d.get("denuncia") is not None else 0
            )
            
            # Verificar se o usuario atual curtiu
            if usuario_email:
                cur.execute(
                    "SELECT 1 FROM forum_curtidas WHERE forum_id = %s AND usuario_email = %s",
                    (post.get_id(), usuario_email)
                )
                if cur.fetchone():
                    post.set_curtido_pelo_usuario(True)
                    
            lista.append(post)
            
        cur.close()
        con.close()
        return lista

    # Respostas de UM post, da mais antiga para a mais nova. Só as ATIVAS (ativo='S'); as ocultadas não aparecem.
    def listar_respostas_por_post(self, forum_id, usuario_email=None):
        con = Conexao.conectar()
        cur = con.cursor(dictionary=True)
        cur.execute(
            "SELECT r.*, COALESCE(u.nickname, u.nome) AS autor_nome FROM forum_respostas r "
            "JOIN usuarios u ON r.autor_email = u.email "
            "WHERE r.forum_id = %s AND r.ativo = 'S' "
            "ORDER BY r.criado_em ASC",
            (forum_id,)
        )
        dados = cur.fetchall()
        
        lista = []
        for d in dados:
            resp = ForumResposta(
                id=d["id"],
                forum_id=d["forum_id"],
                autor_email=d["autor_email"],
                autor_nome=d["autor_nome"],
                texto=d["texto"],
                criado_em=d["criado_em"],
                likes=d["likes"] if d["likes"] is not None else 0,
                ativo=d["ativo"]
            )
            
            # Verificar se o usuario atual curtiu
            if usuario_email:
                cur.execute(
                    "SELECT 1 FROM forum_resposta_curtidas WHERE resposta_id = %s AND usuario_email = %s",
                    (resp.get_id(), usuario_email)
                )
                if cur.fetchone():
                    resp.set_curtido_pelo_usuario(True)
                    
            lista.append(resp)
            
        cur.close()
        con.close()
        return lista

    # INSERT do post. cur.lastrowid devolve o id gerado (AUTO_INCREMENT) e guardamos no objeto.
    def inserir_post(self, forum):
        con = Conexao.conectar()
        cur = con.cursor()
        cur.execute(
            "INSERT INTO forum (autor_id, texto, criado_em, likes) VALUES (%s, %s, NOW(), 0)",
            (forum.get_autor_id(), forum.get_texto())
        )
        con.commit()
        forum.set_id(cur.lastrowid)
        cur.close()
        con.close()

    # INSERT da resposta (começa com 0 likes e ativo='S').
    def inserir_resposta(self, resposta):
        con = Conexao.conectar()
        cur = con.cursor()
        cur.execute(
            "INSERT INTO forum_respostas (forum_id, autor_email, texto, criado_em, likes, ativo) "
            "VALUES (%s, %s, %s, NOW(), 0, 'S')",
            (resposta.get_forum_id(), resposta.get_autor_email(), resposta.get_texto())
        )
        con.commit()
        resposta.set_id(cur.lastrowid)
        cur.close()
        con.close()

    # CURTIR = botão liga/desliga:
    #   já curtiu -> remove o registro em forum_curtidas e DIMINUI o contador (GREATEST(0, ...) impede número negativo)
    #   não curtiu -> insere o registro e AUMENTA o contador
    # Devolve True se a curtida foi adicionada, False se removida.
    def alternar_curtida_post(self, forum_id, usuario_email):
        con = Conexao.conectar()
        cur = con.cursor()
        
        # Verificar se ja curtiu
        cur.execute(
            "SELECT id FROM forum_curtidas WHERE forum_id = %s AND usuario_email = %s",
            (forum_id, usuario_email)
        )
        registro = cur.fetchone()
        
        if registro:
            # Remover curtida
            cur.execute(
                "DELETE FROM forum_curtidas WHERE forum_id = %s AND usuario_email = %s",
                (forum_id, usuario_email)
            )
            cur.execute(
                "UPDATE forum SET likes = GREATEST(0, likes - 1) WHERE id = %s",
                (forum_id,)
            )
            curtida_adicionada = False
        else:
            # Adicionar curtida
            cur.execute(
                "INSERT INTO forum_curtidas (forum_id, usuario_email) VALUES (%s, %s)",
                (forum_id, usuario_email)
            )
            cur.execute(
                "UPDATE forum SET likes = likes + 1 WHERE id = %s",
                (forum_id,)
            )
            curtida_adicionada = True
            
        con.commit()
        cur.close()
        con.close()
        return curtida_adicionada

    # Mesma lógica de liga/desliga, para as respostas (tabela forum_resposta_curtidas).
    def alternar_curtida_resposta(self, resposta_id, usuario_email):
        con = Conexao.conectar()
        cur = con.cursor()
        
        # Verificar se ja curtiu
        cur.execute(
            "SELECT id FROM forum_resposta_curtidas WHERE resposta_id = %s AND usuario_email = %s",
            (resposta_id, usuario_email)
        )
        registro = cur.fetchone()
        
        if registro:
            # Remover curtida
            cur.execute(
                "DELETE FROM forum_resposta_curtidas WHERE resposta_id = %s AND usuario_email = %s",
                (resposta_id, usuario_email)
            )
            cur.execute(
                "UPDATE forum_respostas SET likes = GREATEST(0, likes - 1) WHERE id = %s",
                (resposta_id,)
            )
            curtida_adicionada = False
        else:
            # Adicionar curtida
            cur.execute(
                "INSERT INTO forum_resposta_curtidas (resposta_id, usuario_email) VALUES (%s, %s)",
                (resposta_id, usuario_email)
            )
            cur.execute(
                "UPDATE forum_respostas SET likes = likes + 1 WHERE id = %s",
                (resposta_id,)
            )
            curtida_adicionada = True
            
        con.commit()
        cur.close()
        con.close()
        return curtida_adicionada

    # DENÚNCIA DE RESPOSTA:
    #   1) a resposta existe?  2) não pode denunciar a própria  3) não pode denunciar duas vezes
    #   4) grava a denúncia, conta o total e, se chegou a 3, marca ativo='N' (some da tela)
    # Devolve True se foi inativada agora.
    def denunciar_resposta(self, resposta_id, usuario_email):
        con = Conexao.conectar()
        cur = con.cursor()
        
        # Obter autor_email da resposta
        cur.execute(
            "SELECT autor_email FROM forum_respostas WHERE id = %s",
            (resposta_id,)
        )
        resp_data = cur.fetchone()
        if not resp_data:
            cur.close()
            con.close()
            raise Exception("Resposta não encontrada.")
            
        autor_resposta = resp_data[0]

        if autor_resposta == usuario_email:
            cur.close()
            con.close()
            raise Exception("Você não pode denunciar sua própria resposta.")

        # Verificar se ja denunciou
        cur.execute(
            "SELECT id FROM forum_resposta_denuncia WHERE resposta_id = %s AND usuario_email = %s",
            (resposta_id, usuario_email)
        )
        registro = cur.fetchone()
        
        if not registro:
            # Inserir denuncia na tabela forum_resposta_denuncia
            cur.execute(
                "INSERT INTO forum_resposta_denuncia (resposta_id, usuario_email) VALUES (%s, %s)",
                (resposta_id, usuario_email)
            )

            # Contar denuncias desta resposta
            cur.execute(
                "SELECT COUNT(*) FROM forum_resposta_denuncia WHERE resposta_id = %s",
                (resposta_id,)
            )
            total_denuncias = cur.fetchone()[0]
            
            # Caso a resposta tenha 3 ou mais registros, deve sumir da tela (ativo = 'N')
            if total_denuncias >= 3:
                cur.execute(
                    "UPDATE forum_respostas SET ativo = 'N' WHERE id = %s",
                    (resposta_id,)
                )
                inativada = True
            else:
                inativada = False
            con.commit()
        else:
            inativada = False
            cur.close()
            con.close()
            raise Exception("Você já denunciou esta resposta.")
            
        cur.close()
        con.close()
        return inativada

    # DENÚNCIA DE POST: mesmas travas (post existe, não é o próprio autor, não denunciou antes).
    # Grava em forum_denuncia, recalcula o total e guarda em forum.denuncia. Com 3+ o post fica oculto.
    # Devolve True se passou a ficar oculto.
    def denunciar_post(self, forum_id, usuario_email):
        con = Conexao.conectar()
        cur = con.cursor()
        
        # Obter dados do post
        cur.execute(
            "SELECT autor_id FROM forum WHERE id = %s",
            (forum_id,)
        )
        post_data = cur.fetchone()
        if not post_data:
            cur.close()
            con.close()
            raise Exception("Publicação não encontrada.")
            
        autor_id = post_data[0]
        if autor_id == usuario_email:
            cur.close()
            con.close()
            raise Exception("Você não pode denunciar sua própria publicação.")

        # Verificar se ja denunciou
        cur.execute(
            "SELECT id FROM forum_denuncia WHERE forum_id = %s AND usuario_email = %s",
            (forum_id, usuario_email)
        )
        registro = cur.fetchone()
        
        if not registro:
            # Inserir denuncia na tabela forum_denuncia
            cur.execute(
                "INSERT INTO forum_denuncia (forum_id, usuario_email) VALUES (%s, %s)",
                (forum_id, usuario_email)
            )

            # Contar denuncias deste post
            cur.execute(
                "SELECT COUNT(*) FROM forum_denuncia WHERE forum_id = %s",
                (forum_id,)
            )
            total_denuncias = cur.fetchone()[0]

            # Atualizar a coluna denuncia na tabela forum
            cur.execute(
                "UPDATE forum SET denuncia = %s WHERE id = %s",
                (total_denuncias, forum_id)
            )
            con.commit()
            ocultado = total_denuncias >= 3
        else:
            cur.close()
            con.close()
            raise Exception("Você já denunciou esta publicação.")
            
        cur.close()
        con.close()
        return ocultado
