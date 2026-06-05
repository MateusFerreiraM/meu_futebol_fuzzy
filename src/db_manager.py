import sqlite3
import itertools

DB_PATH = "pelada_fuzzy.db"

def conectar():
    return sqlite3.connect(DB_PATH)

def inicializar_banco():
    """Cria as tabelas no banco de dados para suportar todas as novas funcionalidades."""
    conn = conectar()
    cursor = conn.cursor()
    
    # Tabela principal com todas as estatísticas e mensalidades
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jogadores (
            nome TEXT PRIMARY KEY,
            nota_base REAL,
            gols INTEGER DEFAULT 0,
            assistencias INTEGER DEFAULT 0,
            vitorias INTEGER DEFAULT 0,
            derrotas INTEGER DEFAULT 0,
            mensalista BOOLEAN DEFAULT 0,
            mensalidade_paga BOOLEAN DEFAULT 0
        )
    ''')
    
    # Tabela do Entrosamento (Sinergia)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sinergia (
            jogador1 TEXT,
            jogador2 TEXT,
            jogos_juntos INTEGER DEFAULT 0,
            vitorias_juntos INTEGER DEFAULT 0,
            PRIMARY KEY (jogador1, jogador2)
        )
    ''')
    
    # Tabela de Histórico de Mensalidades
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mensalidade_historico (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ano INTEGER,
            mes INTEGER,
            jogador TEXT,
            mensalista BOOLEAN DEFAULT 0,
            pago BOOLEAN DEFAULT 0,
            UNIQUE(ano, mes, jogador)
        )
    ''')
    
    conn.commit()
    conn.close()

def popular_banco_inicial(nomes_iniciais):
    """Insere os jogadores com valores padrão apenas se o banco estiver vazio."""
    conn = conectar()
    cursor = conn.cursor()
    for nome in nomes_iniciais:
        cursor.execute('''
            INSERT OR IGNORE INTO jogadores 
            (nome, nota_base, gols, assistencias, vitorias, derrotas, mensalista, mensalidade_paga) 
            VALUES (?, 3.0, 0, 0, 0, 0, 0, 0)
        ''', (nome,))
    conn.commit()
    conn.close()

def obter_jogadores():
    """Puxa todos os jogadores e as suas estatísticas completas para o Ranking e Sorteio."""
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM jogadores')
    linhas = cursor.fetchall()
    conn.close()
    
    jogadores = []
    for l in linhas:
        jogadores.append({
            "nome": l[0], 
            "nota_base": l[1],
            "gols": l[2],
            "assistencias": l[3],
            "vitorias": l[4],
            "derrotas": l[5],
            "mensalista": bool(l[6]),
            "mensalidade_paga": bool(l[7])
        })
    return jogadores

def atualizar_estatisticas_jogador(nome, nova_nota, gols_partida, assist_partida, ganhou_partida, empatou_partida=False):
    """
    Atualiza a nota nebulosa e soma as estatísticas da partida atual ao histórico do jogador.
    """
    conn = conectar()
    cursor = conn.cursor()
    
    vitoria_add = 1 if ganhou_partida else 0
    derrota_add = 0 if (ganhou_partida or empatou_partida) else 1
    
    cursor.execute('''
        UPDATE jogadores 
        SET nota_base = ?, 
            gols = gols + ?, 
            assistencias = assistencias + ?, 
            vitorias = vitorias + ?, 
            derrotas = derrotas + ?
        WHERE nome = ?
    ''', (nova_nota, gols_partida, assist_partida, vitoria_add, derrota_add, nome))
    
    conn.commit()
    conn.close()

def gerir_mensalidade(nome, mensalista, pago):
    """Atualiza o status financeiro do jogador."""
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE jogadores SET mensalista = ?, mensalidade_paga = ? WHERE nome = ?
    ''', (int(mensalista), int(pago), nome))
    conn.commit()
    conn.close()

def obter_historico_duplas():
    """Puxa o histórico de panelinhas para o Motor Nebuloso de Sinergia."""
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('SELECT jogador1, jogador2, jogos_juntos, vitorias_juntos FROM sinergia')
    linhas = cursor.fetchall()
    conn.close()
    
    historico = {}
    for l in linhas:
        historico[(l[0], l[1])] = {"jogos": l[2], "vitorias": l[3]}
    return historico

def atualizar_sinergia(jogadores_equipa, ganhou):
    """Recebe os nomes dos jogadores de uma equipa e atualiza o histórico de todos os pares possíveis."""
    conn = conectar()
    cursor = conn.cursor()
    pares = itertools.combinations(jogadores_equipa, 2)
    
    for p1, p2 in pares:
        j1, j2 = sorted([p1, p2])
        cursor.execute('SELECT jogos_juntos, vitorias_juntos FROM sinergia WHERE jogador1 = ? AND jogador2 = ?', (j1, j2))
        resultado = cursor.fetchone()
        
        vitoria_add = 1 if ganhou else 0
        
        if resultado:
            novo_jogos = resultado[0] + 1
            novo_vitorias = resultado[1] + vitoria_add
            cursor.execute('UPDATE sinergia SET jogos_juntos = ?, vitorias_juntos = ? WHERE jogador1 = ? AND jogador2 = ?', 
                           (novo_jogos, novo_vitorias, j1, j2))
        else:
            cursor.execute('INSERT INTO sinergia (jogador1, jogador2, jogos_juntos, vitorias_juntos) VALUES (?, ?, ?, ?)', 
                           (j1, j2, 1, vitoria_add))
            
    conn.commit()
    conn.close()

# --- CRUD de Jogadores ---

def adicionar_jogador(nome, nota_base=3.0):
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO jogadores 
            (nome, nota_base, gols, assistencias, vitorias, derrotas, mensalista, mensalidade_paga) 
            VALUES (?, ?, 0, 0, 0, 0, 0, 0)
        ''', (nome, nota_base))
        conn.commit()
    except sqlite3.IntegrityError:
        pass # Jogador já existe
    finally:
        conn.close()

def remover_jogador(nome):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM jogadores WHERE nome = ?', (nome,))
    cursor.execute('DELETE FROM sinergia WHERE jogador1 = ? OR jogador2 = ?', (nome, nome))
    cursor.execute('DELETE FROM mensalidade_historico WHERE jogador = ?', (nome,))
    conn.commit()
    conn.close()

def editar_jogador(nome_antigo, novo_nome, nova_nota=None):
    conn = conectar()
    cursor = conn.cursor()
    if nova_nota is not None:
        cursor.execute('UPDATE jogadores SET nome = ?, nota_base = ? WHERE nome = ?', (novo_nome, nova_nota, nome_antigo))
    else:
        cursor.execute('UPDATE jogadores SET nome = ? WHERE nome = ?', (novo_nome, nome_antigo))
    
    if nome_antigo != novo_nome:
        cursor.execute('UPDATE sinergia SET jogador1 = ? WHERE jogador1 = ?', (novo_nome, nome_antigo))
        cursor.execute('UPDATE sinergia SET jogador2 = ? WHERE jogador2 = ?', (novo_nome, nome_antigo))
        cursor.execute('UPDATE mensalidade_historico SET jogador = ? WHERE jogador = ?', (novo_nome, nome_antigo))
    
    conn.commit()
    conn.close()

# --- Histórico de Mensalidades ---

def obter_historico_mensalidades(ano, mes):
    """Puxa o histórico de um mês específico."""
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('SELECT jogador, mensalista, pago FROM mensalidade_historico WHERE ano = ? AND mes = ?', (ano, mes))
    linhas = cursor.fetchall()
    conn.close()
    
    historico = {}
    for l in linhas:
        historico[l[0]] = {"mensalista": bool(l[1]), "pago": bool(l[2])}
    return historico

def atualizar_historico_mensalidade(ano, mes, jogador, mensalista, pago):
    """Adiciona ou atualiza o status de um jogador num mês específico."""
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO mensalidade_historico (ano, mes, jogador, mensalista, pago)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(ano, mes, jogador) DO UPDATE SET
            mensalista=excluded.mensalista,
            pago=excluded.pago
    ''', (ano, mes, jogador, int(mensalista), int(pago)))
    conn.commit()
    conn.close()

def resetar_estatisticas():
    """Zera todas as notas (volta para 3.0), gols, assistências, vitórias, derrotas e histórico de sinergia."""
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('UPDATE jogadores SET nota_base = 3.0, gols = 0, assistencias = 0, vitorias = 0, derrotas = 0')
    cursor.execute('DELETE FROM sinergia')
    conn.commit()
    conn.close()