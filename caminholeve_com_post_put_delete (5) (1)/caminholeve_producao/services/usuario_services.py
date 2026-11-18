# usuario_services.py — SERVICE DE USUÁRIO (REGRAS DE NEGÓCIO)
# O Service fica entre o Controller e o DAO. Aqui moram as REGRAS: validações, criptografia
# de senha, limite de tentativas... O Service não sabe nada de HTML nem de SQL:
#   - recebe dados "limpos" do Controller
#   - valida e decide (levanta Exception com a mensagem de erro se algo estiver errado)
#   - pede ao DAO para gravar/buscar no banco.
from dao.usuario_dao import UsuarioDAO
from models.usuario_model import Usuario
# generate_password_hash = transforma a senha em um HASH (embaralhado e irreversível) para guardar no banco.
# check_password_hash    = confere se a senha digitada corresponde ao hash guardado.
# Assim, nem o administrador do banco vê a senha real de ninguém.
from werkzeug.security import generate_password_hash, check_password_hash
import re

# Apelido: 3 a 30 caracteres; letras (com acento), números, ponto, hífen e underline. Sem espaços.
REGEX_NICKNAME = re.compile(r"^[\w.\-]{3,30}$", re.UNICODE)

class UsuarioService:
    def __init__(self):
        self.dao = UsuarioDAO()

    # REGRA DA SENHA FORTE: mínimo 6 caracteres, 1 letra maiúscula e 1 número.
    # Se não cumprir, levanta Exception — e o Controller mostra a mensagem ao usuário.
    # (A mesma regra existe em JavaScript nas telas, mas aqui é a validação que VALE: o navegador pode ser burlado.)
    def validar_requisitos_senha(self, senha):
        if not senha or len(senha) < 6:
            raise Exception("A senha deve ter no mínimo 6 caracteres.")
        if not any(c.isupper() for c in senha):
            raise Exception("A senha deve conter pelo menos uma letra maiúscula (A-Z).")
        if not any(c.isdigit() for c in senha):
            raise Exception("A senha deve conter pelo menos um número (0-9).")

    # REGRA DO APELIDO: formato válido e não pode pertencer a outra conta.
    # email_atual = dono do apelido permitido (na edição de perfil, a pessoa pode manter o próprio).
    # Devolve o apelido já sem espaços nas pontas.
    def validar_nickname(self, nickname, email_atual=None):
        nickname = (nickname or "").strip()
        if not nickname:
            raise Exception("O apelido (nickname) é obrigatório.")
        if not REGEX_NICKNAME.match(nickname):
            raise Exception("O apelido deve ter de 3 a 30 caracteres e usar apenas letras, números, ponto (.), hífen (-) ou underline (_), sem espaços.")
        dono = self.dao.buscar_por_nickname(nickname)
        if dono and dono.get_email() != email_atual:
            raise Exception("Este apelido já está em uso. Escolha outro.")
        return nickname

    # CADASTRO: 1) e-mail já existe? 2) apelido livre? 3) senha forte? 4) gera o hash 5) monta o objeto Usuario 6) manda o DAO gravar.
    def cadastrar(self, email, nome, nickname, cidade, estado, nascimento, tipo, senha):
        # Validação se o usuário já existe
        if self.dao.buscar_por_email(email):
            raise Exception("Este e-mail já está cadastrado no sistema!")

        nickname = self.validar_nickname(nickname)

        # Validar força da senha (mínimo 6 chars, 1 maiúscula, 1 número)
        self.validar_requisitos_senha(senha)
        
        # Criptografar a senha usando hash seguro
        senha_hash = generate_password_hash(senha)
        
        usuario = Usuario(
            email=email,
            nome=nome,
            nickname=nickname,
            cidade=cidade,
            estado=estado,
            nascimento=nascimento,
            tipo=tipo,
            senha=senha_hash
        )
        self.dao.inserir(usuario)

    # Atalho: pede ao DAO o usuário daquele e-mail (ou None se não existir).
    def buscar_por_email(self, email):
        return self.dao.buscar_por_email(email)

    # LOGIN: devolve o Usuario se e-mail+senha estiverem corretos; senão levanta Exception.
    # Repare que a mensagem é a mesma para 'e-mail não existe' e 'senha errada' (não revela qual dos dois falhou).
    def autenticar(self, email, senha):
        usuario = self.dao.buscar_por_email(email)
        if not usuario:
            raise Exception("E-mail ou senha incorretos!")
        
        # Verificar se a senha confere com o hash salvo (ou texto puro legado)
        senha_valida = False
        # OBS.: este try/except tenta aceitar senhas antigas em texto puro. Nas versões atuais do Werkzeug,
        # check_password_hash só devolve False (não dá erro) quando o valor não é um hash, então o 'except' provavelmente
        # nunca roda e os usuários de teste com senha '123456' do caminho.sql não conseguem entrar. Quem se cadastrou pelo site funciona.
        try:
            senha_valida = check_password_hash(usuario.get_senha(), senha)
        except Exception:
            senha_valida = (usuario.get_senha() == senha)

        if not senha_valida:
            raise Exception("E-mail ou senha incorretos!")

        # Verificar se a conta está ativa
        if usuario.get_ativo() == 'N':
            raise Exception("Sua conta foi desativada pelo administrador.")
            
        return usuario

    # Lista todos os usuários (usado pelo painel ADM).
    def listar_todos(self):
        return self.dao.listar_todos()

    # Liga/desliga a conta (ativo S/N).
    def alternar_status(self, email):
        return self.dao.alternar_status(email)

    # Edita nome/apelido/cidade/estado/nascimento. Texto vazio vira None (NULL no banco).
    def atualizar_dados(self, email, nome, nickname, cidade, estado, nascimento):
        if not nome or not nome.strip():
            raise Exception("O nome completo é obrigatório.")

        usuario = self.dao.buscar_por_email(email)
        if not usuario:
            raise Exception("Usuário não encontrado.")

        nickname = self.validar_nickname(nickname, email_atual=email)

        cidade_val = cidade.strip() if cidade and cidade.strip() else None
        estado_val = estado.strip() if estado and estado.strip() else None
        nasc_val = nascimento.strip() if nascimento and str(nascimento).strip() else None

        self.dao.atualizar_dados(
            email=email,
            nome=nome.strip(),
            nickname=nickname,
            cidade=cidade_val,
            estado=estado_val,
            nascimento=nasc_val
        )
        return self.dao.buscar_por_email(email)

    # TROCA DE SENHA logado: valida a regra, confere a confirmação e exige a senha ATUAL correta antes de gravar o novo hash.
    def atualizar_senha(self, email, senha_atual, nova_senha, confirmar_nova_senha):
        if not senha_atual:
            raise Exception("Informe sua senha atual para confirmação.")
        self.validar_requisitos_senha(nova_senha)
        if nova_senha != confirmar_nova_senha:
            raise Exception("A confirmação da nova senha não confere.")

        usuario = self.dao.buscar_por_email(email)
        if not usuario:
            raise Exception("Usuário não encontrado.")

        senha_valida = False
        try:
            senha_valida = check_password_hash(usuario.get_senha(), senha_atual)
        except Exception:
            senha_valida = (usuario.get_senha() == senha_atual)

        if not senha_valida:
            raise Exception("A senha atual informada está incorreta.")

        nova_senha_hash = generate_password_hash(nova_senha)
        self.dao.atualizar_senha(email, nova_senha_hash)

    # RECUPERAÇÃO: monta as 3 perguntas de segurança a partir dos dados do cadastro.
    # Bloqueia quem já errou 3 vezes ou está desativado.
    # Truque: se o usuário NÃO preencheu a cidade/UF/nascimento (campos opcionais), a pergunta é trocada por outra
    # possível de responder (primeiro nome / perfil / ano do cadastro).
    def obter_perguntas_seguranca(self, email):
        usuario = self.dao.buscar_por_email(email)
        if not usuario:
            raise Exception("E-mail não encontrado no sistema.")

        if usuario.get_ativo() == 'N' or usuario.get_erros_recuperacao() >= 3:
            raise Exception("Sua conta está bloqueada por exceder o limite de 3 tentativas ou por ação administrativa. Envie um e-mail para admin@caminholeve.com para solicitar o desbloqueio.")

        perguntas = []
        # Pergunta 1: Cidade ou Primeiro Nome
        if usuario.get_cidade():
            perguntas.append({
                "campo": "cidade",
                "titulo": "1. Qual é a Cidade informada no seu cadastro?",
                "tipo_input": "text",
                "placeholder": "Digite o nome da sua cidade"
            })
        else:
            perguntas.append({
                "campo": "primeiro_nome",
                "titulo": "1. Qual é o seu Primeiro Nome cadastrado?",
                "tipo_input": "text",
                "placeholder": "Digite apenas seu primeiro nome"
            })

        # Pergunta 2: Estado (UF)
        if usuario.get_estado():
            perguntas.append({
                "campo": "estado",
                "titulo": "2. Qual é a sigla do Estado (UF) informado no seu cadastro?",
                "tipo_input": "text",
                "placeholder": "Ex: SP, RJ, MG..."
            })
        else:
            perguntas.append({
                "campo": "perfil",
                "titulo": "2. Qual é o seu Perfil de cadastro (Portador, Familiar ou Outro)?",
                "tipo_input": "text",
                "placeholder": "Digite seu perfil"
            })

        # Pergunta 3: Data de Nascimento ou Ano
        if usuario.get_nascimento():
            perguntas.append({
                "campo": "nascimento",
                "titulo": "3. Qual é a sua Data de Nascimento cadastrada?",
                "tipo_input": "date",
                "placeholder": ""
            })
        else:
            perguntas.append({
                "campo": "ano_criacao",
                "titulo": "3. Em qual Ano você realizou seu cadastro neste portal?",
                "tipo_input": "number",
                "placeholder": "Ex: 2025"
            })

        return perguntas, usuario

    # Confere as respostas das perguntas de segurança.
    # Acertou TODAS -> zera erros e libera. Errou -> soma 1 erro; no 3º erro BLOQUEIA a conta (ativo='N').
    def validar_respostas_seguranca(self, email, respostas):
        usuario = self.dao.buscar_por_email(email)
        if not usuario:
            raise Exception("E-mail não encontrado.")

        if usuario.get_ativo() == 'N' or usuario.get_erros_recuperacao() >= 3:
            raise Exception("Esta conta está bloqueada. Entre em contato com o administrador pelo e-mail admin@caminholeve.com")

        # Biblioteca para tratar acentos.
        import unicodedata
        # Normaliza o texto para comparar: minúsculas, sem espaços nas pontas e SEM ACENTO
        # ('São Paulo' == 'sao paulo'), para o usuário não errar por detalhe de digitação.
        def norm(s):
            if not s: return ""
            nfkd = unicodedata.normalize('NFKD', str(s).strip().lower())
            return "".join([c for c in nfkd if not unicodedata.combining(c)])

        acertos = 0
        total_perguntas = len(respostas)

        for campo, resposta in respostas.items():
            resp_norm = norm(resposta)
            if campo == "cidade":
                correto = norm(usuario.get_cidade())
                if resp_norm == correto and correto != "":
                    acertos += 1
            elif campo == "primeiro_nome":
                primeiro_nome_real = usuario.get_nome().split()[0] if usuario.get_nome() else ""
                if resp_norm == norm(primeiro_nome_real) and primeiro_nome_real != "":
                    acertos += 1
            elif campo == "estado":
                correto = norm(usuario.get_estado())
                if resp_norm == correto and correto != "":
                    acertos += 1
            elif campo == "perfil":
                correto = norm(usuario.get_tipo())
                if resp_norm == correto and correto != "":
                    acertos += 1
            elif campo == "nascimento":
                nasc_real = str(usuario.get_nascimento()) if usuario.get_nascimento() else ""
                if str(resposta).strip() == nasc_real and nasc_real != "":
                    acertos += 1
            elif campo == "ano_criacao":
                ano_real = str(usuario.get_criado_em().year) if usuario.get_criado_em() else ""
                if str(resposta).strip() == ano_real and ano_real != "":
                    acertos += 1

        if acertos == total_perguntas and total_perguntas >= 3:
            # Acertou todas as perguntas!
            self.dao.zerar_erros_recuperacao(email)
            return True, 0, "Identidade confirmada com sucesso!"
        else:
            # Errou
            erros_atuais = self.dao.registrar_erro_recuperacao(email)
            if erros_atuais >= 3:
                self.dao.bloquear_conta_recuperacao(email)
                return False, 3, "🚨 Conta bloqueada! Você errou as perguntas de segurança 3 vezes. Sua conta foi travada por segurança. Por favor, envie um e-mail para o administrador (admin@caminholeve.com) para solicitar o desbloqueio."
            else:
                restantes = 3 - erros_atuais
                return False, erros_atuais, f"Respostas incorretas! Você tem mais {restantes} tentativa(s) antes do bloqueio da sua conta."

    # PASSO FINAL da recuperação: valida a nova senha, grava o hash novo e zera o contador de erros.
    def redefinir_senha_recuperacao(self, email, nova_senha, confirmar_nova_senha):
        self.validar_requisitos_senha(nova_senha)
        if nova_senha != confirmar_nova_senha:
            raise Exception("A confirmação da nova senha não confere.")

        usuario = self.dao.buscar_por_email(email)
        if not usuario:
            raise Exception("Usuário não encontrado.")

        if usuario.get_ativo() == 'N':
            raise Exception("Sua conta está bloqueada. Entre em contato com admin@caminholeve.com")

        nova_senha_hash = generate_password_hash(nova_senha)
        self.dao.atualizar_senha(email, nova_senha_hash)
        self.dao.zerar_erros_recuperacao(email)
