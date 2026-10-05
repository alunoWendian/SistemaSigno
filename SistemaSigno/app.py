import sqlite3
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Nome do seu arquivo de banco existente
NOME_DO_BANCO = 'DescubraSigno.db'  # Ajuste com o nome exato do seu arquivo .db

def conectar_banco():
    conn = sqlite3.connect(NOME_DO_BANCO)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/descobrir-signo', methods=['POST'])
def processar_signo():
    dados = request.get_json()
    nome = dados.get('nome')
    email = dados.get('email')
    data_nascimento = dados.get('data_nascimento') # Formato: 'YYYY-MM-DD'
    
    if not nome or not email or not data_nascimento:
        return jsonify({'sucesso': False, 'mensagem': 'Preencha todos os campos!'}), 400
        
    ano, mes, dia = map(int, data_nascimento.split('-'))
    
    conn = conectar_banco()
    cursor = conn.cursor()
    
    try:
        # 1. Busca os dados do Signo
        cursor.execute('''
            SELECT ID_signo, nome_signo, elemento, planeta_regente 
            FROM signo 
            WHERE (mes_inicio = ? AND dia_inicio <= ?) 
               OR (mes_fim = ? AND dia_fim >= ?)
        ''', (mes, dia, mes, dia))
        
        signo_info = cursor.fetchone()
        
        if not signo_info:
            conn.close()
            return jsonify({'sucesso': False, 'mensagem': 'Signo não encontrado.'}), 404
            
        id_signo, nome_signo, elemento, planeta_regente = signo_info
        
        # 2. Busca TODAS as Características ligadas a este ID_signo na tabela 'caracteristica'
        cursor.execute('''
            SELECT descricao, tipo 
            FROM caracteristica 
            WHERE ID_signo = ?
        ''', (id_signo,))
        
        # Cria uma lista de dicionários com cada característica encontrada
        caracteristicas_rows = cursor.fetchall()
        lista_caracteristicas = [
            {'descricao': row[0], 'tipo': row[1]} for row in caracteristicas_rows
        ]
        
        # 3. Registra o usuário apontando para o ID_signo
        cursor.execute('''
            INSERT INTO usuario (nome, data_nascimento, email, ID_signo)
            VALUES (?, ?, ?, ?)
        ''', (nome, data_nascimento, email, id_signo))
        
        conn.commit()
        conn.close()
        
        # 4. Retorna a resposta completa incluindo a lista de características
        return jsonify({
            'sucesso': True,
            'usuario': nome,
            'signo': {
                'nome': nome_signo,
                'elemento': elemento,
                'planeta': planeta_regente,
                'caracteristicas': lista_caracteristicas  # Envia as características para o Frontend!
            }
        })

    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'sucesso': False, 'mensagem': 'Este e-mail já está cadastrado!'}), 400
    except Exception as e:
        conn.close()
        return jsonify({'sucesso': False, 'mensagem': f'Erro no servidor: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)