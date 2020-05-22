import sqlite3

conn = sqlite3.connect('devall.db')

cursor = conn.cursor()

cursor.execute("""
create table if not exists votacoes(
    titulo VARCHAR(80) NOT NULL PRIMARY KEY
);""")
cursor.execute("""
create table if not exists alternativas(
    opcao VARCHAR(80) NOT NULL,
    votacao VARCHAR(80),
    PRIMARY KEY (opcao, votacao),
    FOREIGN KEY (votacao) REFERENCES votacoes(id) 
);""")
cursor.execute("""
create table if not exists votos(
    nome VARCHAR(80),
    opcao VARCHAR(80),
    votacao VARCHAR(80),
    PRIMARY KEY (nome, votacao),
    FOREIGN KEY (opcao, votacao) REFERENCES alternativas(opcao, votacao)
)""")

print("Conectado ao banco de dados")