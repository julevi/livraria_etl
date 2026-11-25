import json
import os
import sqlite3
from datetime import datetime
from decimal import Decimal

# ---------- 1. EXTRAÇÃO ----------
def api_falsa(page, page_size):
    """Finge ser uma API paginada: devolve um 'pedaço' da lista."""
    with open("dados/livros.json", encoding="utf-8") as f:
        todos = json.load(f)
    total_pages = (len(todos) + page_size - 1) // page_size
    inicio = (page - 1) * page_size
    return {"page": page, "total_pages": total_pages, "items": todos[inicio:inicio + page_size]}


def extrair(page_size=3):
    registros = []
    page = 1
    total_pages = 1
    while page <= total_pages:
        resposta = api_falsa(page, page_size)
        registros.extend(resposta["items"])
        total_pages = resposta["total_pages"]
        page += 1
    print(f"extracao: paginas={total_pages} registros_brutos={len(registros)}")

    os.makedirs("brutos", exist_ok=True)
    with open("brutos/livros.json", "w", encoding="utf-8") as f:
        json.dump(registros, f, ensure_ascii=False, indent=1)
    return registros


# ---------- 2. TRANSFORMAÇÃO ----------
def converter_preco(valor):
    """39.9 -> Decimal('39.90') | '29,50' -> Decimal('29.50')"""
    texto = str(valor).replace(",", ".")
    return Decimal(texto).quantize(Decimal("0.01"))


def converter_data(texto):
    """'2024-03-10' fica igual | '15/07/2024' -> '2024-07-15'"""
    if "/" in texto:
        return datetime.strptime(texto, "%d/%m/%Y").strftime("%Y-%m-%d")
    return texto


def padronizar_autor(nome):
    """'machado de assis' -> 'Machado De Assis'"""
    return nome.title()


def remover_repetidos(registros):
    """Mantém a primeira ocorrência de cada id."""
    vistos = set()
    unicos = []
    for r in registros:
        if r["id"] not in vistos:
            vistos.add(r["id"])
            unicos.append(r)
    return unicos


def transformar(registros):
    unicos = remover_repetidos(registros)
    limpos = []
    for r in unicos:
        limpos.append({
            "id": r["id"],
            "titulo": r["titulo"],
            "autor": padronizar_autor(r["autor"]),
            "preco": converter_preco(r["preco"]),
            "lancado_em": converter_data(r["lancado_em"]),
        })
    print(f"transformacao: unicos={len(unicos)} repetidos_descartados={len(registros) - len(unicos)}")
    return limpos

# ---------- 3. CARGA ----------
def carregar(livros, banco="livraria.db"):
    con = sqlite3.connect(banco)
    con.execute("""CREATE TABLE IF NOT EXISTS livros (
        id INTEGER PRIMARY KEY, titulo TEXT, autor TEXT, preco NUMERIC, lancado_em TEXT)""")
    con.execute("DELETE FROM livros")  # idempotência: limpa antes de carregar
    for l in livros:
        con.execute(
            "INSERT INTO livros (id, titulo, autor, preco, lancado_em) VALUES (?, ?, ?, ?, ?)",
            (l["id"], l["titulo"], l["autor"], str(l["preco"]), l["lancado_em"]),
        )
    con.commit()
    total = con.execute("SELECT COUNT(*) FROM livros").fetchone()[0]
    con.close()
    print(f"carga: livros={total}")

# ---------- 4. RECONCILIAÇÃO ----------
def reconciliar(livros, banco="livraria.db"):
    con = sqlite3.connect(banco)
    qtd_destino, soma_destino = con.execute("SELECT COUNT(*), SUM(preco) FROM livros").fetchone()
    con.close()
    soma_origem = sum(l["preco"] for l in livros)
    diferenca = abs(soma_origem - Decimal(str(soma_destino)).quantize(Decimal("0.01")))
    print(f"reconciliacao: qtd_origem={len(livros)} qtd_destino={qtd_destino} "
          f"soma_origem={soma_origem} soma_destino={soma_destino:.2f} diferenca={diferenca}")

if __name__ == "__main__":
    brutos = extrair()
    limpos = transformar(brutos)
    carregar(limpos)
    reconciliar(limpos)