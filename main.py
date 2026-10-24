import psycopg2
from ofxparse import OfxParser

# Conecta ao banco de dados criado no DBeaver.
conexao = psycopg2.connect(
    host="localhost",
    port=5432,
    database="desafio1910",
    user="postgres",
    password="8741"
)

try:
    with open("extrato.ofx", "rb") as arquivo:
        ofx = OfxParser.parse(arquivo)

    transacoes = ofx.account.statement.transactions

    print("EXTRATO BANCÁRIO")

    for t in transacoes:
        print(f"""
Data        : {t.date.strftime('%d/%m/%Y')}
Valor       : R$ {t.amount:.2f}
Descrição   : {t.memo}
--------------------------------------
""")

    entradas = sum(t.amount for t in transacoes if t.amount > 0)
    saidas = sum(t.amount for t in transacoes if t.amount < 0)
    saldo = entradas + saidas

    print("--------------------------------------")
    print(f"Total de transações: {len(transacoes)}")
    print(f"Entradas: R$ {entradas:.2f}")
    print(f"Saídas: R$ {saidas:.2f}")
    print(f"Saldo: R$ {saldo:.2f}")
    print("--------------------------------------")

    inseridas = 0

    with conexao.cursor() as cursor:
        for t in transacoes:
            cursor.execute(
                """
                INSERT INTO movimentacoes
                    (data_movimentacao, valor, descricao, fitid)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (fitid) DO NOTHING
                """,
                (
                    t.date.date(),
                    t.amount,
                    (t.memo or "")[:255],
                    t.id
                )
            )
            inseridas += cursor.rowcount

    conexao.commit()
    print(f"Novas transações salvas no PostgreSQL: {inseridas}")

finally:
    conexao.close()
