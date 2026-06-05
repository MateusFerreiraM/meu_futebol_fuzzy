import streamlit as st

def injetar_css_tema():
    """Injeta o CSS customizado para o tema futebolístico (Mobile-First / Dark Mode)."""
    st.markdown("""
        <style>
            /* Reset e Base */
            .stApp {
                background-color: #0d1b2a; /* Azul escuro profundo, remetendo a jogos à noite */
                color: #e0e1dd;
            }
            
            /* Títulos */
            h1, h2, h3 {
                color: #4CAF50 !important; /* Verde Gramado */
                font-family: 'Inter', sans-serif;
                font-weight: 800;
                text-transform: uppercase;
                text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
            }
            
            /* Botões */
            .stButton > button {
                background: linear-gradient(135deg, #4CAF50, #2E7D32) !important;
                color: white !important;
                border-radius: 20px !important;
                border: none !important;
                padding: 10px 24px !important;
                font-weight: bold !important;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3) !important;
                transition: transform 0.1s, box-shadow 0.1s !important;
                width: 100%; /* Mobile First: botões ocupam largura total */
            }
            .stButton > button:active {
                transform: scale(0.95) !important;
                box-shadow: 0 2px 3px rgba(0, 0, 0, 0.3) !important;
            }
            
            /* Cards de Jogadores */
            .player-card {
                background: rgba(255, 255, 255, 0.05);
                border-left: 4px solid #4CAF50;
                border-radius: 8px;
                padding: 10px;
                margin-bottom: 8px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                box-shadow: 0 2px 4px rgba(0,0,0,0.2);
            }
            
            .player-name {
                font-size: 16px;
                font-weight: bold;
                color: #ffffff;
            }
            
            .player-stats {
                font-size: 12px;
                color: #aaaaaa;
            }
            
            .player-rating {
                background: #4CAF50;
                color: white;
                padding: 4px 8px;
                border-radius: 12px;
                font-weight: bold;
                font-size: 14px;
            }
            
            /* Inputs e Selects */
            .stSelectbox div[data-baseweb="select"], .stTextInput input, .stNumberInput input {
                border-radius: 10px !important;
                background-color: rgba(255, 255, 255, 0.1) !important;
                color: white !important;
            }
            
            /* Tabs */
            .stTabs [data-baseweb="tab-list"] {
                gap: 2px;
                background-color: transparent;
            }
            .stTabs [data-baseweb="tab"] {
                border-radius: 8px 8px 0 0;
                padding: 8px 16px;
                color: #aaaaaa;
            }
            .stTabs [aria-selected="true"] {
                background-color: rgba(76, 175, 80, 0.2);
                border-bottom: 2px solid #4CAF50;
                color: #4CAF50;
                font-weight: bold;
            }
        </style>
    """, unsafe_allow_html=True)

def renderizar_card_jogador(nome, nota, gols=None, assist=None):
    """Renderiza um card visual de um jogador usando HTML/CSS."""
    stats_html = ""
    if gols is not None and assist is not None:
        stats_html = f"<div class='player-stats'>Gols: {gols} | Assist: {assist}</div>"
        
    html = f"<div class='player-card' style='margin-bottom: 5px;'><div><div class='player-name' style='font-size: 1.1rem; margin-bottom: 2px;'>{nome}</div>{stats_html}</div><div class='player-rating'>{nota:.1f}</div></div>"
    st.markdown(html, unsafe_allow_html=True)
