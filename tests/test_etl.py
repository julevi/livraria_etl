from decimal import Decimal
from etl import converter_preco, converter_data, remover_repetidos


def test_preco_com_virgula_vira_numero():
    assert converter_preco("29,50") == Decimal("29.50")


def test_data_brasileira_vira_iso():
    assert converter_data("15/07/2024") == "2024-07-15"


def test_repetidos_sao_removidos():
    entrada = [{"id": 1}, {"id": 2}, {"id": 1}]
    assert len(remover_repetidos(entrada)) == 2