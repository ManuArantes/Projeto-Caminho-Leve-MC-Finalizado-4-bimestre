# aplicar.py — executa um arquivo .sql de migração no banco configurado em dao/conexao.py.
# Uso (na pasta do projeto):  python migracoes/aplicar.py migracoes/001_nickname.sql
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dao.conexao import Conexao


def aplicar(caminho):
    with open(caminho, encoding="utf-8") as f:
        # Remove comentários de linha e separa os comandos pelo ';'
        linhas = [l for l in f.read().splitlines() if not l.strip().startswith("--")]
    comandos = [c.strip() for c in "\n".join(linhas).split(";") if c.strip()]

    con = Conexao.conectar()
    cur = con.cursor()
    for comando in comandos:
        cur.execute(comando)
    con.commit()
    cur.close()
    con.close()
    print(f"OK: {len(comandos)} comando(s) aplicado(s) de {caminho}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python migracoes/aplicar.py <arquivo.sql>")
        sys.exit(1)
    aplicar(sys.argv[1])
