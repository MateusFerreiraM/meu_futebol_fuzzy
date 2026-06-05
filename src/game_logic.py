import itertools
from .fuzzy_engine import calcular_bonus_sinergia

def calcular_forca_equipa(equipa, historico_duplas):
    """Calcula a força somando as notas individuais + o Bónus de Sinergia Nebulosa."""
    forca_individual = sum(j["nota_base"] for j in equipa)
    bonus_total = 0.0
    
    if len(equipa) > 1:
        pares = itertools.combinations(equipa, 2)
        for p1, p2 in pares:
            par_nome = tuple(sorted([p1["nome"], p2["nome"]]))
            if par_nome in historico_duplas:
                dados = historico_duplas[par_nome]
                if dados["jogos"] > 0:
                    taxa = (dados["vitorias"] / dados["jogos"]) * 100
                    bonus_total += calcular_bonus_sinergia(dados["jogos"], taxa)
                
    return forca_individual + bonus_total

def organizar_times_dinamico(jogadores_presentes, num_times, historico_duplas):
    """Algoritmo Guloso (Greedy) para balancear os times."""
    times = [[] for _ in range(num_times)]
    
    # Ordena os jogadores do melhor para o pior
    jogadores_ordenados = sorted(jogadores_presentes, key=lambda x: x["nota_base"], reverse=True)

    for jogador in jogadores_ordenados:
        melhor_time_idx = 0
        menor_forca_resultante = float('inf')

        # Testa o jogador em todos os times disponíveis
        for i in range(num_times):
            time_teste = times[i] + [jogador]
            forca_teste = calcular_forca_equipa(time_teste, historico_duplas)

            if forca_teste < menor_forca_resultante:
                menor_forca_resultante = forca_teste
                melhor_time_idx = i

        times[melhor_time_idx].append(jogador)

    return times