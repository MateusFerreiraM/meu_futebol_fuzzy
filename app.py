import streamlit as st
import pandas as pd
import time
from datetime import datetime
import streamlit.components.v1 as components
from src.db_manager import (
    inicializar_banco, popular_banco_inicial, obter_jogadores, 
    atualizar_estatisticas_jogador, obter_historico_duplas, atualizar_sinergia,
    adicionar_jogador, remover_jogador, editar_jogador, 
    obter_historico_mensalidades, atualizar_historico_mensalidade,
    resetar_estatisticas
)
from src.game_logic import organizar_times_dinamico, calcular_forca_equipa
from src.fuzzy_engine import calcular_delta_nota
from src.ui_components import injetar_css_tema, renderizar_card_jogador

st.set_page_config(page_title="Fuzzy Soccer", page_icon="⚽", layout="wide")
injetar_css_tema()

# --- INICIALIZAÇÃO ---
inicializar_banco()
nomes = ["João", "Marcos", "Pedro", "Lucas", "Mateus", "Tiago", "André", "Felipe", 
         "Davi", "Bruno", "Carlos", "Daniel", "Eduardo", "Gabriel", "Henrique"]
popular_banco_inicial(nomes)

if 'admin' not in st.session_state: st.session_state.admin = False
if 'partida' not in st.session_state:
    st.session_state.partida = {'status': 'config'}

# --- LOGIN ---
with st.sidebar:
    st.title("🔐 Acesso")
    if not st.session_state.admin:
        pin = st.text_input("PIN do Organizador", type="password")
        if st.button("Entrar", use_container_width=True):
            if pin == "1234":
                st.session_state.admin = True
                st.rerun()
            else: st.error("PIN incorreto!")
    else:
        st.success("Modo: ORGANIZADOR")
        if st.button("Sair", use_container_width=True):
            st.session_state.admin = False
            st.rerun()

todos_jogadores = obter_jogadores()
historico_duplas = obter_historico_duplas()
nomes_todos = [j["nome"] for j in todos_jogadores]

st.title("⚽ Fuzzy Soccer Draft")
aba_sorteio, aba_partida, aba_ranking, aba_gestao, aba_financas = st.tabs([
    "🎲 Sorteio", "⏱️ Partida Ao Vivo", "🏆 Ranking", "⚙️ Gestão", "💰 Finanças"
])

# ==========================================
# 1. ABA DE SORTEIO
# ==========================================
with aba_sorteio:
    st.header("Organizar Pelada")
    jogadores_hoje = st.multiselect("Quem veio jogar hoje?", nomes_todos, default=nomes_todos[:12])
    
    col1, col2 = st.columns(2)
    with col1: num_times = st.number_input("Número de Equipas", min_value=2, max_value=8, value=2)
    with col2: jog_por_time = st.number_input("Jogadores por Equipa", min_value=1, max_value=11, value=5)

    if st.session_state.admin and st.button("Sortear Equipas", type="primary"):
        lista_presentes = [j for j in todos_jogadores if j["nome"] in jogadores_hoje]
        total_vagas = num_times * jog_por_time
        lista_presentes = sorted(lista_presentes, key=lambda x: x['nota_base'], reverse=True)[:total_vagas]
        
        times = organizar_times_dinamico(lista_presentes, num_times, historico_duplas)
        st.session_state.times_sorteados = times
        st.success("Sorteio Concluído! Vá para a aba 'Partida Ao Vivo'.")

    if 'times_sorteados' in st.session_state:
        st.divider()
        cols = st.columns(num_times)
        for i, time_arr in enumerate(st.session_state.times_sorteados):
            forca = calcular_forca_equipa(time_arr, historico_duplas)
            with cols[i]:
                st.markdown(f"<h3 style='text-align: center;'>Equipa {i+1} <br><small style='color: #4CAF50;'>⭐ {forca:.1f}</small></h3>", unsafe_allow_html=True)
                for j in time_arr:
                    renderizar_card_jogador(j['nome'], j['nota_base'])

# ==========================================
# 2. ABA PARTIDA AO VIVO (TEMPO REAL)
# ==========================================
with aba_partida:
    st.header("Painel de Jogo")
    p = st.session_state.partida

    if 'times_sorteados' not in st.session_state:
        st.warning("Faça o sorteio primeiro.")
    elif not st.session_state.admin:
        st.info("🔒 Apenas o organizador gere o cronómetro e placar.")
    else:
        if p['status'] == 'config':
            st.subheader("⚙️ Quadro Tático")
            n_equipas = [f"Equipa {i+1}" for i in range(len(st.session_state.times_sorteados))]
            
            c1, c2 = st.columns(2)
            with c1: eqA_sel = st.selectbox("Equipa Base - Lado A", n_equipas, index=0)
            with c2: eqB_sel = st.selectbox("Equipa Base - Lado B", n_equipas, index=1 if len(n_equipas)>1 else 0)
            
            idxA = int(eqA_sel.split(" ")[1]) - 1
            idxB = int(eqB_sel.split(" ")[1]) - 1
            
            default_A = [j['nome'] for j in st.session_state.times_sorteados[idxA]]
            default_B = [j['nome'] for j in st.session_state.times_sorteados[idxB]]
            
            key_A = f"ms_A_{eqA_sel}"
            key_B = f"ms_B_{eqB_sel}"
            
            # Obtém a escalação atual. Se o usuário ainda não mexeu, usa a default.
            current_A = st.session_state.get(key_A, default_A)
            current_B = st.session_state.get(key_B, default_B)
            
            # O "Banco" são todos os jogadores que não estão atualmente no Lado A nem no Lado B
            banco = [n for n in nomes_todos if n not in current_A and n not in current_B]
            
            # Opções de cada lado = Seus próprios jogadores + Jogadores que estão no Banco
            options_A = current_A + banco
            options_B = current_B + banco
            
            st.divider()
            st.markdown("<h4 style='text-align: center; color: #4CAF50;'>🔄 Ajustes de Escalação</h4>", unsafe_allow_html=True)
            
            c3, c4 = st.columns(2)
            with c3:
                draft_A = st.multiselect(f"Jogadores ({eqA_sel})", options=options_A, default=current_A, key=key_A)
            with c4:
                draft_B = st.multiselect(f"Jogadores ({eqB_sel})", options=options_B, default=current_B, key=key_B)
                
            st.divider()
            st.markdown("<h4 style='text-align: center;'>Configurações da Partida</h4>", unsafe_allow_html=True)
            c5, c6 = st.columns(2)
            with c5: max_min = st.number_input("Duração (Minutos)", min_value=1, value=10)
            with c6: max_gols = st.number_input("Acaba em quantos golos?", min_value=1, value=2)
            
            if st.button("⏱️ Começar Partida", type="primary", use_container_width=True):
                if len(draft_A) == 0 or len(draft_B) == 0:
                    st.error("As equipas não podem estar vazias!")
                else:
                    st.session_state.partida = {
                        'status': 'andamento',
                        'nomeA': eqA_sel, 'nomeB': eqB_sel,
                        'jogadoresA': draft_A,
                        'jogadoresB': draft_B,
                        'placarA': 0, 'placarB': 0,
                        'max_gols': max_gols, 'max_minutos': max_min,
                        'inicio': time.time(),
                        'eventos': []
                    }
                    st.rerun()

        elif p['status'] == 'andamento':
            placar_html = f"""
            <div style="display: flex; justify-content: space-around; align-items: center; background: rgba(255,255,255,0.05); padding: 15px; border-radius: 15px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.3);">
                <div style="text-align: center; width: 40%;">
                    <div style="font-size: 3rem; font-weight: bold; color: #4CAF50; line-height: 1;">{p['placarA']}</div>
                    <div style="font-size: 1.2rem; font-weight: bold; color: #fff; margin-top: 5px; text-transform: uppercase;">{p['nomeA']}</div>
                </div>
                <div style="font-size: 2.5rem; font-weight: bold; color: #aaaaaa; text-shadow: 1px 1px 2px rgba(0,0,0,0.5);">X</div>
                <div style="text-align: center; width: 40%;">
                    <div style="font-size: 3rem; font-weight: bold; color: #4CAF50; line-height: 1;">{p['placarB']}</div>
                    <div style="font-size: 1.2rem; font-weight: bold; color: #fff; margin-top: 5px; text-transform: uppercase;">{p['nomeB']}</div>
                </div>
            </div>
            """
            st.markdown(placar_html, unsafe_allow_html=True)
            
            st.divider()
            
            inicio_js = p['inicio'] * 1000
            duracao_js = p['max_minutos'] * 60 * 1000
            
            html_timer = f"""
            <div id="timer" style="font-size:3rem; font-weight:bold; text-align:center; font-family:'Inter', sans-serif; color:#ffffff; background: rgba(0,0,0,0.5); border-radius: 10px; padding: 10px;"></div>
            <script>
            var start = {inicio_js};
            var duration = {duracao_js};
            var timer = setInterval(function() {{
                var now = Date.now();
                var elapsed = now - start;
                var rem = Math.floor((duration - elapsed) / 1000);
                
                if (rem <= 0) {{ 
                    clearInterval(timer); 
                    document.getElementById("timer").innerHTML = "00:00"; 
                    document.getElementById("timer").style.color = "red"; 
                }} else {{
                    var m = Math.floor(rem / 60); 
                    var s = rem % 60;
                    document.getElementById("timer").innerHTML = (m<10?"0"+m:m) + ":" + (s<10?"0"+s:s);
                }}
            }}, 500);
            </script>
            """
            components.html(html_timer, height=120)

            st.subheader("⚽ Lançar Golo")
            cg1, cg2, cg3 = st.columns(3)
            with cg1: time_gol = st.selectbox("Qual equipa marcou?", [p['nomeA'], p['nomeB']])
            lista_autores = p['jogadoresA'] if time_gol == p['nomeA'] else p['jogadoresB']
            with cg2: autor = st.selectbox("Quem fez?", lista_autores)
            with cg3: assist = st.selectbox("Assistência?", ["Ninguém"] + [j for j in lista_autores if j != autor])

            if st.button("💥 REGISTAR GOLO!"):
                p['eventos'].append({'autor': autor, 'assist': assist if assist != "Ninguém" else None, 'time': time_gol})
                if time_gol == p['nomeA']: p['placarA'] += 1
                else: p['placarB'] += 1
                
                if p['placarA'] >= p['max_gols'] or p['placarB'] >= p['max_gols']:
                    st.session_state.partida['status'] = 'encerrada'
                    st.session_state.partida['processado'] = False
                st.rerun()

            st.divider()
            if st.button("🛑 Encerrar Partida Agora", type="secondary", use_container_width=True):
                st.session_state.partida['status'] = 'encerrada'
                st.session_state.partida['processado'] = False
                st.rerun()

        elif p['status'] == 'encerrada':
            if not p.get('processado', False):
                ganhouA = p['placarA'] > p['placarB']
                ganhouB = p['placarB'] > p['placarA']
                empatou = p['placarA'] == p['placarB']

                def processar_time(jogadores, ganhou):
                    for jog_nome in jogadores:
                        gols = sum(1 for ev in p['eventos'] if ev['autor'] == jog_nome)
                        assists = sum(1 for ev in p['eventos'] if ev['assist'] == jog_nome)
                        
                        impacto = gols + assists
                        saldo = 1 if ganhou else (0 if empatou else -1)
                        
                        delta = calcular_delta_nota(impacto, saldo)
                        nota_ant = next((j["nota_base"] for j in todos_jogadores if j["nome"] == jog_nome), 3.0)
                        nova_nota = max(1.0, min(5.0, nota_ant + delta))
                        
                        atualizar_estatisticas_jogador(jog_nome, nova_nota, gols, assists, ganhou, empatou)
                
                processar_time(p['jogadoresA'], ganhouA)
                processar_time(p['jogadoresB'], ganhouB)
                
                if ganhouA: 
                    atualizar_sinergia(p['jogadoresA'], True)
                    atualizar_sinergia(p['jogadoresB'], False)
                elif ganhouB:
                    atualizar_sinergia(p['jogadoresB'], True)
                    atualizar_sinergia(p['jogadoresA'], False)
                
                p['processado'] = True

            st.success("🏁 PARTIDA ENCERRADA E ESTATÍSTICAS SALVAS!")
            
            placar_html = f"""
            <div style="display: flex; justify-content: space-around; align-items: center; background: rgba(76, 175, 80, 0.1); border: 2px solid #4CAF50; padding: 20px; border-radius: 15px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.3);">
                <div style="text-align: center; width: 40%;">
                    <div style="font-size: 4rem; font-weight: bold; color: #4CAF50; line-height: 1;">{p['placarA']}</div>
                    <div style="font-size: 1.5rem; font-weight: bold; color: #fff; margin-top: 5px; text-transform: uppercase;">{p['nomeA']}</div>
                </div>
                <div style="font-size: 2.5rem; font-weight: bold; color: #aaaaaa; text-shadow: 1px 1px 2px rgba(0,0,0,0.5);">X</div>
                <div style="text-align: center; width: 40%;">
                    <div style="font-size: 4rem; font-weight: bold; color: #4CAF50; line-height: 1;">{p['placarB']}</div>
                    <div style="font-size: 1.5rem; font-weight: bold; color: #fff; margin-top: 5px; text-transform: uppercase;">{p['nomeB']}</div>
                </div>
            </div>
            """
            st.markdown(placar_html, unsafe_allow_html=True)
            
            st.subheader("📊 Resumo dos Eventos")
            if not p['eventos']:
                st.write("Nenhum gol marcado nesta partida.")
            else:
                for ev in p['eventos']:
                    time_nome = ev.get('time', 'Desconhecido')
                    txt = f"<div style='background: rgba(255,255,255,0.05); padding: 10px; border-radius: 8px; margin-bottom: 8px; border-left: 4px solid #4CAF50;'>"
                    txt += f"⚽ <b>{ev['autor']}</b> <span style='color: #aaaaaa; font-size: 0.9rem;'>({time_nome})</span>"
                    if ev['assist']: 
                        txt += f" <br><small style='color: #aaaaaa; margin-left: 20px;'>👟 Assistência: <b>{ev['assist']}</b></small>"
                    txt += "</div>"
                    st.markdown(txt, unsafe_allow_html=True)

            st.divider()
            if st.button("🔄 Organizar Nova Partida", type="primary", use_container_width=True):
                st.session_state.partida = {'status': 'config'}
                st.rerun()

# ==========================================
# 3. ABA RANKING
# ==========================================
with aba_ranking:
    st.header("🏆 Tabela de Classificação")
    df = pd.DataFrame(todos_jogadores)
    if not df.empty:
        df = df[['nome', 'nota_base', 'vitorias', 'derrotas', 'gols', 'assistencias']]
        # Arredondar a nota e encurtar nomes das colunas
        df['nota_base'] = df['nota_base'].round(1)
        df = df.rename(columns={
            'nome': 'Jogador',
            'nota_base': 'Nota',
            'vitorias': 'V',
            'derrotas': 'D',
            'gols': 'Gols',
            'assistencias': 'Assist'
        })
        df = df.sort_values(by='Nota', ascending=False).reset_index(drop=True)
        df.index += 1
        st.dataframe(df, use_container_width=True)
        
    st.divider()
    st.subheader("⚠️Resetar Estatísticas⚠️")
    st.write("Isso apagará todas as vitórias, derrotas, gols e assistências do banco de dados, e voltará as notas de todos os jogadores para 3.0.")
    confirma = st.checkbox("Tenho certeza que quero apagar todas as estatísticas e voltar notas para 3.0")
    if st.button("Zerar Estatísticas", type="primary", disabled=not confirma):
        resetar_estatisticas()
        st.success("Todas as notas, gols, assistências, vitórias e derrotas foram zeradas com sucesso!")
        time.sleep(1)
        st.rerun()

# ==========================================
# 4. ABA GESTÃO JOGADORES (CRUD)
# ==========================================
with aba_gestao:
    st.header("⚙️ Gestão de Jogadores")
    if not st.session_state.admin:
        st.info("🔒 Apenas o organizador pode gerir jogadores.")
    else:
        c1, c2, c3 = st.columns(3)
        with c1:
            st.subheader("➕ Adicionar")
            novo_nome = st.text_input("Nome do Jogador")
            nova_nota = st.number_input("Nota Inicial", min_value=1.0, max_value=5.0, value=3.0, step=0.5)
            if st.button("Criar Jogador", use_container_width=True):
                if novo_nome and novo_nome not in nomes_todos:
                    adicionar_jogador(novo_nome, nova_nota)
                    st.success(f"{novo_nome} adicionado!")
                    time.sleep(1)
                    st.rerun()
                elif novo_nome in nomes_todos:
                    st.error("Jogador já existe!")
                    
        with c2:
            st.subheader("✏️ Editar")
            jog_edit = st.selectbox("Selecionar", nomes_todos, key="edit_sel")
            novo_nome_edit = st.text_input("Novo Nome", value=jog_edit if jog_edit else "")
            if st.button("Salvar Edição", use_container_width=True):
                if jog_edit:
                    editar_jogador(jog_edit, novo_nome_edit)
                    st.success("Atualizado!")
                    time.sleep(1)
                    st.rerun()
                    
        with c3:
            st.subheader("🗑️ Remover")
            jog_rem = st.selectbox("Selecionar", nomes_todos, key="rem_sel")
            if st.button("Deletar Jogador", type="primary", use_container_width=True):
                if jog_rem:
                    remover_jogador(jog_rem)
                    st.success("Removido!")
                    time.sleep(1)
                    st.rerun()

# ==========================================
# 5. ABA MENSALIDADES
# ==========================================
with aba_financas:
    st.header("💰 Gestão Financeira")
    mes_atual = datetime.now().month
    ano_atual = datetime.now().year
    
    c1, c2 = st.columns(2)
    with c1: sel_mes = st.number_input("Mês", 1, 12, mes_atual)
    with c2: sel_ano = st.number_input("Ano", 2000, 2100, ano_atual)
    
    historico_mes = obter_historico_mensalidades(sel_ano, sel_mes)
    
    if st.session_state.admin:
        st.write("Atualize os pagamentos marcando os checkboxes abaixo:")
        dados_fin = []
        for j in todos_jogadores:
            nome = j["nome"]
            hist = historico_mes.get(nome, {"mensalista": j["mensalista"], "pago": False})
            dados_fin.append({
                "Jogador": nome,
                "Mensalista?": hist["mensalista"],
                "Pago?": hist["pago"]
            })
            
        df_fin = pd.DataFrame(dados_fin)
        edited_df = st.data_editor(
            df_fin, 
            hide_index=True, 
            disabled=["Jogador"],
            use_container_width=True,
            key=f"editor_{sel_ano}_{sel_mes}"
        )
        
        if st.button("💾 Salvar Alterações do Mês", type="primary"):
            for i, row in edited_df.iterrows():
                atualizar_historico_mensalidade(sel_ano, sel_mes, row["Jogador"], row["Mensalista?"], row["Pago?"])
            st.success("Histórico salvo!")
    else:
        st.info("🔒 Apenas o organizador pode ver e editar pagamentos.")