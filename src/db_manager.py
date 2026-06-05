import os
import streamlit as st
from supabase import create_client, Client

@st.cache_resource
def get_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

def obter_jogadores():
    supabase = get_supabase()
    res = supabase.table("jogadores").select("*").execute()
    jogadores = []
    for row in res.data:
        jogadores.append({
            "nome": row["nome"],
            "nota_base": row.get("nota_base", 3.0),
            "vitorias": row.get("vitorias", 0),
            "derrotas": row.get("derrotas", 0),
            "gols": row.get("gols", 0),
            "assistencias": row.get("assistencias", 0),
            "mensalista": bool(row.get("mensalista", False))
        })
    return jogadores

def obter_todos_jogadores():
    return obter_jogadores()

def atualizar_estatisticas_jogador(nome, nova_nota, gols_partida, assist_partida, ganhou_partida, empatou_partida=False):
    supabase = get_supabase()
    res = supabase.table("jogadores").select("gols, assistencias, vitorias, derrotas").eq("nome", nome).execute()
    if res.data:
        row = res.data[0]
        v_add = 1 if ganhou_partida else 0
        d_add = 0 if (ganhou_partida or empatou_partida) else 1
        
        supabase.table("jogadores").update({
            "nota_base": nova_nota,
            "gols": row.get("gols", 0) + gols_partida,
            "assistencias": row.get("assistencias", 0) + assist_partida,
            "vitorias": row.get("vitorias", 0) + v_add,
            "derrotas": row.get("derrotas", 0) + d_add
        }).eq("nome", nome).execute()

def obter_historico_duplas():
    supabase = get_supabase()
    res = supabase.table("sinergia").select("*").execute()
    historico = []
    for row in res.data:
        historico.append({
            "jogador1": row["jogador1"],
            "jogador2": row["jogador2"],
            "jogos_juntos": row.get("jogos_juntos", 0),
            "vitorias_juntos": row.get("vitorias_juntos", 0)
        })
    return historico

def atualizar_sinergia(jogadores_time, ganhou):
    supabase = get_supabase()
    for i in range(len(jogadores_time)):
        for j in range(i + 1, len(jogadores_time)):
            j1, j2 = sorted([jogadores_time[i], jogadores_time[j]])
            res = supabase.table("sinergia").select("jogos_juntos, vitorias_juntos").eq("jogador1", j1).eq("jogador2", j2).execute()
            if res.data:
                row = res.data[0]
                supabase.table("sinergia").update({
                    "jogos_juntos": row.get("jogos_juntos", 0) + 1,
                    "vitorias_juntos": row.get("vitorias_juntos", 0) + (1 if ganhou else 0)
                }).eq("jogador1", j1).eq("jogador2", j2).execute()
            else:
                supabase.table("sinergia").insert({
                    "jogador1": j1,
                    "jogador2": j2,
                    "jogos_juntos": 1,
                    "vitorias_juntos": 1 if ganhou else 0
                }).execute()

def adicionar_jogador(nome, nota_base=3.0):
    supabase = get_supabase()
    try:
        supabase.table("jogadores").insert({"nome": nome, "nota_base": nota_base}).execute()
    except Exception as e:
        print(f"Erro ao adicionar jogador: {e}")

def remover_jogador(nome):
    supabase = get_supabase()
    supabase.table("jogadores").delete().eq("nome", nome).execute()

def editar_jogador(nome_antigo, nome_novo):
    supabase = get_supabase()
    supabase.table("jogadores").update({"nome": nome_novo}).eq("nome", nome_antigo).execute()

def obter_historico_mensalidades(ano, mes):
    supabase = get_supabase()
    res = supabase.table("mensalidade_historico").select("*").eq("ano", ano).eq("mes", mes).execute()
    historico = {}
    for row in res.data:
        historico[row["jogador"]] = {
            "mensalista": bool(row.get("mensalista", False)),
            "pago": bool(row.get("pago", False))
        }
    return historico

def atualizar_historico_mensalidade(ano, mes, jogador, mensalista, pago):
    supabase = get_supabase()
    supabase.table("mensalidade_historico").upsert({
        "ano": ano,
        "mes": mes,
        "jogador": jogador,
        "mensalista": mensalista,
        "pago": pago
    }).execute()

def salvar_status_mensalidade(mes_str, estado_mensalidade):
    pass

def resetar_estatisticas():
    supabase = get_supabase()
    supabase.table("jogadores").update({
        "nota_base": 3.0, 
        "gols": 0, 
        "assistencias": 0, 
        "vitorias": 0, 
        "derrotas": 0
    }).neq("nome", "N/A").execute()
    
    supabase.table("sinergia").delete().neq("jogador1", "N/A").execute()

def inicializar_banco():
    pass

def popular_banco_inicial(nomes_iniciais):
    pass