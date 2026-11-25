# Livraria — ETL de exemplo

Pipeline ETL simples em Python que lê um catálogo de livros com dados "sujos",
padroniza os registros e carrega o resultado em um banco SQLite.

## Etapas

1. **Extração** — simula uma API paginada lendo `dados/livros.json` e salva os
   registros brutos em `brutos/livros.json`.
2. **Transformação**
   - remove registros com `id` repetido (mantém a primeira ocorrência);
   - converte preços como `"29,50"` para `Decimal("29.50")`;
   - converte datas `dd/mm/aaaa` para ISO (`aaaa-mm-dd`);
   - padroniza o nome do autor (`"machado de assis"` → `"Machado De Assis"`).
3. **Carga** — grava na tabela `livros` de `livraria.db` (limpa a tabela antes,
   então rodar várias vezes dá o mesmo resultado).
4. **Reconciliação** — compara quantidade e soma de preços entre origem e destino.

## Como rodar

Requer Python 3.10+.

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate

pip install -r requirements.txt
python etl.py
```

Saída esperada:

```
extracao: paginas=3 registros_brutos=7
transformacao: unicos=6 repetidos_descartados=1
carga: livros=6
reconciliacao: qtd_origem=6 qtd_destino=6 soma_origem=207.60 soma_destino=207.60 diferenca=0.00
```

## Testes

```bash
pytest
```

## Estrutura

```
.
├── dados/livros.json   # dados de entrada
├── etl.py              # pipeline
└── tests/test_etl.py   # testes das funções de transformação
```

`brutos/` e `livraria.db` são gerados ao rodar o script e não vão para o repositório.
