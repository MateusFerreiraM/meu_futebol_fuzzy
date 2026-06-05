import pytest

@pytest.fixture
def jogadores_mock():
    return [
        {"nome": "Alice", "nota_base": 8.0},
        {"nome": "Bob", "nota_base": 7.5},
        {"nome": "Charlie", "nota_base": 6.0},
        {"nome": "David", "nota_base": 9.0},
    ]

@pytest.fixture
def historico_duplas_mock():
    return {
        ("Alice", "Bob"): {"jogos": 10, "vitorias": 8},
        ("Charlie", "David"): {"jogos": 5, "vitorias": 1},
        ("Alice", "David"): {"jogos": 0, "vitorias": 0},
    }
