# usuario_dao.py — DAO DE USUÁRIO (Data Access Object)
# O DAO é a ÚNICA camada que escreve SQL. Cada método abre conexão, executa um comando,
# (faz commit se for alteração), fecha tudo e devolve o resultado como objeto Model.
# Padrão de TODOS os métodos de DAO:
#    con = Conexao.conectar()   -> abre a conexão
#    cur = con.cursor(...)      -> cursor = quem executa os comandos SQL
#    cur.execute(SQL, (valores,)) -> os %s são preenchidos pelos valores: protege contra SQL INJECTION
#    con.commit()               -> CONFIRMA alterações (INSERT/UPDATE/DELETE); SELECT não precisa
#    cur.close(); con.close()   -> libera os recursos
from dao.conexao import Conexao
from models.usuario_model import Usuario

class UsuarioDAO:

    # SELECT de um usuário pelo e-mail. dictionary=True faz cada linha vir como dicionário (d["nome"]).
    # Devolve um objeto Usuario, ou None se não existir.
    def buscar_por_email(self, email):
        con = Conexao.conectar()
        cur = con.cursor(dictionary=True)
        cur.execute("SELECT * FROM usuarios WHERE email=%s", (email,))
        d = cur.fetchone()
        cur.close()
        con.close()
        if d:
            return self._montar_usuario(d)
        return None

    # Converte uma linha (dicionário) da tabela usuarios em objeto Usuario.
    def _montar_usuario(self, d):
        return Usuario(
            email=d["email"],
            nome=d["nome"],
            nickname=d.get("nickname"),
            cidade=d["cidade"],
            estado=d["estado"],
            nascimento=d["nascimento"],
            tipo=d["tipo"],
            senha=d["senha"],
            criado_em=d["criado_em"],
            ativo=d.get("ativo", "S"),
            erros_recuperacao=d.get("erros_recuperacao", 0)
        )

    # Busca pelo apelido. A collation do banco ignora maiúsculas e acentos, então
    # "Ana" encontra "ana". Usado para impedir apelidos repetidos.
    def buscar_por_nickname(self, nickname):
        con = Conexao.conectar()
        cur = con.cursor(dictionary=True)
        cur.execute("SELECT * FROM usuarios WHERE nickname=%s", (nickname,))
        d = cur.fetchone()
        cur.close()
        con.close()
        return self._montar_usuario(d) if d else None

    # Todos os usuários, do mais novo para o mais antigo (usado no painel ADM).
    def listar_todos(self):
        con = Conexao.conectar()
        cur = con.cursor(dictionary=True)
        cur.execute("SELECT * FROM usuarios ORDER BY criado_em DESC")
        dados = cur.fetchall()
        cur.close()
        con.close()

        lista = []
        for d in dados:
            lista.append(self._montar_usuario(d))
        return lista

    # Inverte ativo S<->N. Ao REATIVAR uma conta também zera erros_recuperacao,
    # ou seja, é assim que o ADM DESBLOQUEIA quem errou as perguntas de segurança.
    def alternar_status(self, email):
        con = Conexao.conectar()
        cur = con.cursor(dictionary=True)
        cur.execute("SELECT ativo FROM usuarios WHERE email=%s", (email,))
        row = cur.fetchone()
        if not row:
            cur.close()
            con.close()
            raise Exception("Usuário não encontrado.")

        novo_status = 'N' if row.get("ativo") == 'S' else 'S'
        if novo_status == 'S':
            cur.execute("UPDATE usuarios SET ativo='S', erros_recuperacao=0 WHERE email=%s", (email,))
        else:
            cur.execute("UPDATE usuarios SET ativo='N' WHERE email=%s", (email,))
        con.commit()
        cur.close()
        con.close()
        return novo_status

    # Soma 1 ao contador de erros (COALESCE trata NULL como 0) e devolve o novo total.
    def registrar_erro_recuperacao(self, email):
        con = Conexao.conectar()
        cur = con.cursor(dictionary=True)
        cur.execute("UPDATE usuarios SET erros_recuperacao = COALESCE(erros_recuperacao, 0) + 1 WHERE email=%s", (email,))
        con.commit()
        cur.execute("SELECT erros_recuperacao FROM usuarios WHERE email=%s", (email,))
        row = cur.fetchone()
        cur.close()
        con.close()
        return row["erros_recuperacao"] if row else 1

    # Bloqueio por 3 erros: ativo='N'. A conta só volta quando o ADM reativar.
    def bloquear_conta_recuperacao(self, email):
        con = Conexao.conectar()
        cur = con.cursor()
        cur.execute("UPDATE usuarios SET ativo='N', erros_recuperacao=3 WHERE email=%s", (email,))
        con.commit()
        cur.close()
        con.close()

    # Zera o contador (após acertar as perguntas ou redefinir a senha).
    def zerar_erros_recuperacao(self, email):
        con = Conexao.conectar()
        cur = con.cursor()
        cur.execute("UPDATE usuarios SET erros_recuperacao=0 WHERE email=%s", (email,))
        con.commit()
        cur.close()
        con.close()

    # INSERT de um novo usuário. NOW() = data/hora atual do servidor MySQL. A senha já chega como hash.
    def inserir(self, usuario):
        con = Conexao.conectar()
        cur = con.cursor()
        cur.execute(
            "INSERT INTO usuarios (email, nome, nickname, cidade, estado, nascimento, tipo, senha, criado_em, ativo) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), %s)",
            (usuario.get_email(), usuario.get_nome(), usuario.get_nickname(), usuario.get_cidade(),
             usuario.get_estado(), usuario.get_nascimento(), usuario.get_tipo(),
             usuario.get_senha(), usuario.get_ativo())
        )
        con.commit()
        cur.close()
        con.close()

    # UPDATE dos dados pessoais (WHERE email=... garante que só mexe nesse usuário).
    def atualizar_dados(self, email, nome, nickname, cidade, estado, nascimento):
        con = Conexao.conectar()
        cur = con.cursor()
        cur.execute(
            "UPDATE usuarios SET nome=%s, nickname=%s, cidade=%s, estado=%s, nascimento=%s WHERE email=%s",
            (nome, nickname, cidade, estado, nascimento, email)
        )
        con.commit()
        cur.close()
        con.close()

    # UPDATE do hash da senha.
    def atualizar_senha(self, email, nova_senha_hash):
        con = Conexao.conectar()
        cur = con.cursor()
        cur.execute(
            "UPDATE usuarios SET senha=%s WHERE email=%s",
            (nova_senha_hash, email)
        )
        con.commit()
        cur.close()
        con.close()
