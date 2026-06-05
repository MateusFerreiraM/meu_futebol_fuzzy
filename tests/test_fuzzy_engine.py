import pytest
from src.fuzzy_engine import calcular_delta_nota, calcular_bonus_sinergia

def test_calcular_delta_nota_alto_positivo():
    delta = calcular_delta_nota(5, 3) # impacto alto, saldo positivo
    assert delta > 0.5

def test_calcular_delta_nota_baixo_negativo():
    delta = calcular_delta_nota(1, -3) # impacto baixo, saldo negativo
    assert delta < -0.5

def test_calcular_delta_nota_medio_neutro():
    delta = calcular_delta_nota(3, 0) # impacto medio, saldo neutro
    assert -0.5 <= delta <= 0.5

def test_calcular_bonus_sinergia_alta_alta():
    bonus = calcular_bonus_sinergia(20, 100) # freq alta, taxa alta
    assert bonus > 0.8

def test_calcular_bonus_sinergia_baixa():
    bonus = calcular_bonus_sinergia(2, 20) # freq baixa, taxa baixa
    assert bonus < 0.4
