# ⚽ Fuzzy Soccer Draft

O **Fuzzy Soccer Draft** é um sistema web inteligente, focado em dispositivos móveis, desenhado para gerir peladas (futebol amador). Seu grande diferencial é a utilização de **Lógica Nebulosa (Fuzzy Logic)** para avaliar o desempenho contínuo dos jogadores e realizar o sorteio perfeito de equipes equilibradas.

## 🚀 Funcionalidades Principais

- **🎲 Sorteio Inteligente com Sinergia:** O sistema divide os times utilizando um algoritmo guloso combinado com notas individuais. Além do "nível" individual, um *Motor Fuzzy de Sinergia* avalia a compatibilidade das duplas que caem no mesmo time, equilibrando a partida com base no histórico de entrosamento.
- **📱 Painel de Jogo (Live Match):** Uma interface mobile-friendly com cronômetro em tempo real, placar visual com flexbox e um "Quadro Tático" interativo para fazer transferências e escalações de última hora antes da bola rolar.
- **🧠 Motor Fuzzy de Avaliação:** Após cada partida, o sistema analisa o impacto do jogador (Gols + Assistências) e o resultado coletivo (Vitória, Empate ou Derrota). As notas não oscilam de forma arbitrária; um conjunto de regras heurísticas Fuzzy garante que jogadores não sejam severamente punidos por derrotas se tiverem jogado muito bem, ou recompensados se tiverem sido carregados ("mochilas").
- **💰 Gestão Financeira:** Controle de pagamento de mensalidades dos jogadores cadastrados mês a mês.
- **📈 Ranking Dinâmico:** Tabela de classificação em tempo real contendo Vitórias, Derrotas, Gols, Assistências e a evolução da Nota de cada jogador.

## 🛠️ Tecnologias Utilizadas

- **Linguagem:** Python 3.10+
- **Interface Gráfica:** Streamlit (com componentes HTML/CSS customizados)
- **Matemática e IA:** `scikit-fuzzy`, `numpy`, `pandas`
- **Banco de Dados:** Supabase (PostgreSQL na nuvem)
- **Testes Unitários:** `pytest`

## ⚙️ Como Instalar e Rodar

1. **Clone o repositório:**
```bash
git clone https://github.com/MateusFerreiraM/meu_futebol_fuzzy.git
cd meu_futebol_fuzzy
```

2. **Crie e ative um ambiente virtual:**
```bash
# Windows
python -m venv .venv
.\.venv\Scripts\activate

# Linux/Mac
python3 -m venv .venv
source .venv/bin/activate
```

3. **Instale as dependências:**
```bash
pip install -r requirements.txt
```

4. **Configure o Banco de Dados (Supabase):**
Crie uma pasta chamada `.streamlit` na raiz do projeto e dentro dela crie um arquivo `secrets.toml` com as suas chaves do Supabase:
```toml
SUPABASE_URL = "Sua URL do Supabase"
SUPABASE_KEY = "Sua chave anon / public"
```
*(Certifique-se de ter rodado o script `supabase_schema.sql` no painel do Supabase para criar as tabelas).*

5. **Inicie a Aplicação:**
```bash
streamlit run app.py
```
O navegador abrirá automaticamente em `http://localhost:8501`.

## 🧪 Rodando os Testes

O projeto conta com uma suíte de testes implementada com `pytest` para garantir a integridade da separação dos times e dos cálculos Fuzzy.
Para rodar, no terminal (com o ambiente ativado), execute:
```bash
pytest tests/
```

## 📂 Estrutura do Projeto

```text
meu_futebol_fuzzy/
├── app.py                # Ponto de entrada do App (Interface Streamlit)
├── requirements.txt      # Dependências do Python
├── pytest.ini            # Configurações do Pytest
├── src/
│   ├── db_manager.py     # Gestão, CRUD e Conexão com o Supabase
│   ├── fuzzy_engine.py   # Lógica Nebulosa (Notas e Sinergia)
│   ├── game_logic.py     # Algoritmo de Sorteio Guloso
│   └── ui_components.py  # Renderização de CSS e Cards customizados
└── tests/
    ├── conftest.py       # Fixtures Mockadas do pytest
    ├── test_fuzzy_engine.py
    └── test_game_logic.py
```
