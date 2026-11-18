# conexao.py — CONEXÃO COM O BANCO DE DADOS
# Todos os DAOs chamam Conexao.conectar() sempre que precisam falar com o MySQL.
# Centralizar aqui evita repetir host/usuário/senha em todo lugar:
# se o banco mudar, você altera só este arquivo.
# ATENÇÃO: o usuário/senha do MySQL estão escritos aqui (hoje password="senha"). Ajuste para a senha do SEU MySQL antes de rodar.

# Biblioteca oficial do MySQL para Python (pip install mysql-connector-python).
import mysql.connector
class Conexao:
    
    @staticmethod
    def conectar():
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="senha",
            database="caminho_leve_mc"
        )
