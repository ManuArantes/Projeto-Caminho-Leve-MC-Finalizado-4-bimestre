# Representa uma pessoa cadastrada no site.
# usuario_model.py — MODEL (modelo) do USUÁRIO
# Um Model é só uma classe que representa uma linha de uma tabela, aqui a tabela `usuarios`.
# Ele NÃO conversa com o banco e NÃO tem regra de negócio: apenas guarda os dados.
# Padrão usado em todos os models do projeto:
#   - atributos PRIVADOS (self.__nome, com dois underscores) -> ENCAPSULAMENTO (POO)
#   - métodos get_xxx() para LER e set_xxx() para ALTERAR cada atributo.
class Usuario:
    # Construtor: recebe os dados (todos opcionais, valor padrão None) e guarda nos atributos privados.
    # tipo  -> 'Portador', 'Outros' ou 'ADM' (administrador)
    # senha -> NUNCA a senha pura: aqui fica o HASH (texto embaralhado, irreversível)
    # ativo -> 'S' conta ativa, 'N' desativada/bloqueada
    # erros_recuperacao -> quantas vezes errou as perguntas de segurança (3 = bloqueio)
    # nickname -> apelido público exibido no site (fórum, relatos, saudação). Pode ser None em contas antigas.
    def __init__(self, email=None, nome=None, cidade=None, estado=None,
                 nascimento=None, tipo=None, senha=None, criado_em=None, ativo='S', erros_recuperacao=0,
                 nickname=None):
        self.__email = email
        self.__nome = nome
        self.__nickname = nickname
        self.__cidade = cidade
        self.__estado = estado
        self.__nascimento = nascimento
        self.__tipo = tipo
        self.__senha = senha
        self.__criado_em = criado_em
        self.__ativo = ativo if ativo is not None else 'S'
        self.__erros_recuperacao = erros_recuperacao if erros_recuperacao is not None else 0

    # GETTERS: leitura dos atributos privados (uma linha cada, só devolvem o valor).
    def get_email(self): return self.__email
    def get_nome(self): return self.__nome
    def get_nickname(self): return self.__nickname
    # Nome mostrado publicamente: o apelido, ou o nome completo se a conta ainda não tiver apelido.
    def get_nome_exibicao(self): return self.__nickname or self.__nome
    def get_cidade(self): return self.__cidade
    def get_estado(self): return self.__estado
    def get_nascimento(self): return self.__nascimento
    def get_tipo(self): return self.__tipo
    def get_senha(self): return self.__senha
    def get_criado_em(self): return self.__criado_em
    def get_ativo(self): return self.__ativo
    def get_erros_recuperacao(self): return self.__erros_recuperacao

    # SETTERS: alteração dos atributos privados.
    def set_email(self, v): self.__email = v
    def set_nome(self, v): self.__nome = v
    def set_nickname(self, v): self.__nickname = v
    def set_cidade(self, v): self.__cidade = v
    def set_estado(self, v): self.__estado = v
    def set_nascimento(self, v): self.__nascimento = v
    def set_tipo(self, v): self.__tipo = v
    def set_senha(self, v): self.__senha = v
    def set_criado_em(self, v): self.__criado_em = v
    def set_ativo(self, v): self.__ativo = v
