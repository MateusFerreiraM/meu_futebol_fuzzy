import pytest
from src.game_logic import calcular_forca_equipa, organizar_times_dinamico

def test_calcular_forca_equipa_sem_sinergia(jogadores_mock):
    equipa = [jogadores_mock[0], jogadores_mock[3]] # Alice e David
    forca = calcular_forca_equipa(equipa, {})
    assert forca == 8.0 + 9.0

def test_calcular_forca_equipa_com_sinergia(jogadores_mock, historico_duplas_mock):
    equipa = [jogadores_mock[0], jogadores_mock[1]] # Alice e Bob
    forca = calcular_forca_equipa(equipa, historico_duplas_mock)
    assert forca > 8.0 + 7.5 # Deve incluir bonus de sinergia

def test_organizar_times_dinamico(jogadores_mock, historico_duplas_mock):
    times = organizar_times_dinamico(jogadores_mock, 2, historico_duplas_mock)
    assert len(times) == 2
    assert len(times[0]) == 2
    assert len(times[1]) == 2
    
    jogadores_distribuidos = [j["nome"] for time in times for j in time]
    assert set(jogadores_distribuidos) == {"Alice", "Bob", "Charlie", "David"}
