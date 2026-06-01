import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'rpg_dados.db')

def conectar():
    return sqlite3.connect(DB_PATH)

def inicializar_banco():
    conn = conectar()
    cursor = conn.cursor()
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS itens (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT NOT NULL, foto TEXT NOT NULL, valor_npc REAL NOT NULL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS hunts (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT NOT NULL, shiny TEXT, angry TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS hunt_itens (hunt_id INTEGER, item_id INTEGER, FOREIGN KEY(hunt_id) REFERENCES hunts(id), FOREIGN KEY(item_id) REFERENCES itens(id))''')
    
    # ATUALIZAÇÃO: Coluna 'mobs' adicionada!
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hunt_id INTEGER,
            tempo TEXT NOT NULL,
            mobs INTEGER,
            shinies INTEGER,
            angrys INTEGER,
            crystais INTEGER,
            crystal_shiny_1 TEXT,
            crystal_shiny_2 TEXT,
            data_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(hunt_id) REFERENCES hunts(id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessao_itens (
            sessao_id INTEGER,
            item_id INTEGER,
            quantidade INTEGER,
            FOREIGN KEY(sessao_id) REFERENCES sessoes(id),
            FOREIGN KEY(item_id) REFERENCES itens(id)
        )
    ''')
    
    conn.commit()
    conn.close()

# --- FUNÇÕES DE ITENS E HUNTS ---
def item_existe(nome):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM itens WHERE LOWER(nome) = LOWER(?)", (nome,))
    return cursor.fetchone() is not None

def adicionar_item(nome, foto, valor_npc):
    if item_existe(nome): return False
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO itens (nome, foto, valor_npc) VALUES (?, ?, ?)', (nome, foto, valor_npc))
    conn.commit()
    conn.close()
    return True

def get_todos_itens():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, foto FROM itens ORDER BY nome")
    itens = cursor.fetchall()
    conn.close()
    return itens

def get_item_por_id(item_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, foto, valor_npc FROM itens WHERE id = ?", (item_id,))
    item = cursor.fetchone()
    conn.close()
    return item

def atualizar_item(item_id, nome, foto, valor_npc):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM itens WHERE LOWER(nome) = LOWER(?) AND id != ?", (nome, item_id))
    if cursor.fetchone():
        conn.close()
        return False 
    cursor.execute('UPDATE itens SET nome = ?, foto = ?, valor_npc = ? WHERE id = ?', (nome, foto, valor_npc, item_id))
    conn.commit()
    conn.close()
    return True

def adicionar_hunt(nome, shiny, angry, itens_ids):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO hunts (nome, shiny, angry) VALUES (?, ?, ?)", (nome, shiny, angry))
    hunt_id = cursor.lastrowid 
    for item_id in itens_ids:
        cursor.execute("INSERT INTO hunt_itens (hunt_id, item_id) VALUES (?, ?)", (hunt_id, item_id))
    conn.commit()
    conn.close()

def get_todas_hunts():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome FROM hunts ORDER BY nome")
    hunts = cursor.fetchall()
    conn.close()
    return hunts

def get_hunt_por_id(hunt_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, shiny, angry FROM hunts WHERE id = ?", (hunt_id,))
    hunt = cursor.fetchone()
    conn.close()
    return hunt

def get_itens_da_hunt(hunt_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT item_id FROM hunt_itens WHERE hunt_id = ?", (hunt_id,))
    itens = [row[0] for row in cursor.fetchall()]
    conn.close()
    return set(itens)

def atualizar_hunt(hunt_id, nome, shiny, angry, itens_ids):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('UPDATE hunts SET nome = ?, shiny = ?, angry = ? WHERE id = ?', (nome, shiny, angry, hunt_id))
    cursor.execute('DELETE FROM hunt_itens WHERE hunt_id = ?', (hunt_id,))
    for item_id in itens_ids:
        cursor.execute("INSERT INTO hunt_itens (hunt_id, item_id) VALUES (?, ?)", (hunt_id, item_id))
    conn.commit()
    conn.close()
    return True

# --- FUNÇÕES DE SESSÕES ---
def get_itens_completos_da_hunt(hunt_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT i.id, i.nome, i.foto 
        FROM itens i
        JOIN hunt_itens hi ON i.id = hi.item_id
        WHERE hi.hunt_id = ?
        ORDER BY i.nome
    ''', (hunt_id,))
    itens = cursor.fetchall()
    conn.close()
    return itens

def adicionar_sessao(hunt_id, tempo, mobs, shinies, angrys, crystais, c_shiny_1, c_shiny_2, itens_quantidades):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO sessoes (hunt_id, tempo, mobs, shinies, angrys, crystais, crystal_shiny_1, crystal_shiny_2)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (hunt_id, tempo, mobs, shinies, angrys, crystais, c_shiny_1, c_shiny_2))
    
    sessao_id = cursor.lastrowid
    
    for item_id, qtd in itens_quantidades.items():
        if qtd > 0:
            cursor.execute("INSERT INTO sessao_itens (sessao_id, item_id, quantidade) VALUES (?, ?, ?)", (sessao_id, item_id, qtd))
            
    conn.commit()
    conn.close()

inicializar_banco()