import sqlite3
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
DB_NAME = 'database.db'

def init_db():
    """Inicializa o banco de dados SQLite e insere os signos padrões caso não existam."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Ativa foreign keys
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    # Criação das tabelas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS signo (
            ID_signo INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_signo TEXT NOT NULL,
            dia_inicio INTEGER NOT NULL,
            mes_inicio INTEGER NOT NULL,
            dia_fim INTEGER NOT NULL,
            mes_fim INTEGER NOT NULL,
            elemento TEXT,
            planeta_regente TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuario (
            ID_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            data_nascimento TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            data_cadastro TEXT DEFAULT (datetime('now', 'localtime')),
            ID_signo INTEGER,
            FOREIGN KEY (ID_signo) REFERENCES signo(ID_signo) ON DELETE SET NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS caracteristica (
            ID_caracteristica INTEGER PRIMARY KEY AUTOINCREMENT,
            descricao TEXT NOT NULL,
            tipo TEXT,
            ID_signo INTEGER NOT NULL,
            FOREIGN KEY (ID_signo) REFERENCES signo(ID_signo) ON DELETE CASCADE
        )
    ''')
    
    # Verifica se a tabela signo já possui dados
    cursor.execute("SELECT COUNT(*) FROM signo")
    if cursor.fetchone()[0] == 0:
        signos_iniciais = [
            ('Áries', 21, 3, 19, 4, 'Fogo', 'Marte'),
            ('Touro', 20, 4, 20, 5, 'Terra', 'Vênus'),
            ('Gêmeos', 21, 5, 20, 6, 'Ar', 'Mercúrio'),
            ('Câncer', 21, 6, 22, 7, 'Água', 'Lua'),
            ('Leão', 23, 7, 22, 8, 'Fogo', 'Sol'),
            ('Virgem', 23, 8, 22, 9, 'Terra', 'Mercúrio'),
            ('Libra', 23, 9, 22, 10, 'Ar', 'Vênus'),
            ('Escorpião', 23, 10, 21, 11, 'Água', 'Plutão'),
            ('Sagitário', 22, 11, 21, 12, 'Fogo', 'Júpiter'),
            ('Capricórnio', 22, 12, 19, 1, 'Terra', 'Saturno'),
            ('Aquário', 20, 1, 18, 2, 'Ar', 'Urano'),
            ('Peixes', 19, 2, 20, 3, 'Água', 'Netuno')
        ]
        cursor.executemany('''
            INSERT INTO signo (nome_signo, dia_inicio, mes_inicio, dia_fim, mes_fim, elemento, planeta_regente)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', signos_iniciais)
        
    conn.commit()
    conn.close()

def descobrir_signo(dia, mes):
    """Lógica SQL para identificar o signo de acordo com o dia e mês."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    query = '''
        SELECT ID_signo, nome_signo, elemento, planeta_regente 
        FROM signo 
        WHERE (mes_inicio = ? AND dia_inicio <= ?) 
           OR (mes_fim = ? AND dia_fim >= ?)
    '''
    cursor.execute(query, (mes, dia, mes, dia))
    resultado = cursor.fetchone()
    conn.close()
    return resultado

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/descobrir-signo', methods=['POST'])
def processar_signo():
    dados = request.get_json()
    nome = dados.get('nome')
    email = dados.get('email')
    data_nascimento = dados.get('data_nascimento') # Formato 'YYYY-MM-DD'
    
    if not nome or not email or not data_nascimento:
        return jsonify({'sucesso': False, 'mensagem': 'Preencha todos os campos!'}), 400
        
    ano, mes, dia = map(int, data_nascimento.split('-'))
    
    # Busca o signo no banco
    signo_info = descobrir_signo(dia, mes)
    
    if not signo_info:
        return jsonify({'sucesso': False, 'mensagem': 'Signo não encontrado para esta data.'}), 404
        
    id_signo, nome_signo, elemento, planeta_regente = signo_info
    
    # Salva ou atualiza o usuário no banco
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")
        
        cursor.execute('''
            INSERT INTO usuario (nome, data_nascimento, email, ID_signo)
            VALUES (?, ?, ?, ?)
        ''', (nome, data_nascimento, email, id_signo))
        
        conn.commit()
        conn.close()
    except sqlite3.IntegrityError:
        return jsonify({'sucesso': False, 'mensagem': 'Este e-mail já está cadastrado!'}), 400
    except Exception as e:
        return jsonify({'sucesso': False, 'mensagem': f'Erro ao salvar usuário: {str(e)}'}), 500
        
    return jsonify({
        'sucesso': True,
        'usuario': nome,
        'signo': {
            'nome': nome_signo,
            'elemento': elemento,
            'planeta': planeta_regente
        }
    })

if __name__ == '__main__':
    init_db()
    print("Servidor rodando em: http://127.0.0.1:5000")
    app.run(debug=True)