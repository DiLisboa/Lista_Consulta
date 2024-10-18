import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash



def get_db_connection():
    conn = sqlite3.connect('bancopsi.db')
    conn.row_factory = sqlite3.Row
    return conn


app = Flask(__name__)
app.secret_key = 'estacio'

@app.route('/')
def lista_pacientes():
    if 'usuario_logado' not in session or session['usuario_logado'] is None:
        return redirect('/login?proxima=lista_pacientes')

    conn = get_db_connection()

    lista_espera = conn.execute(""" SELECT id, horario, data, nome_paciente, nome_psicologo FROM lista_espera """).fetchall()

    conn.close()

    return render_template('lista_horarios.html', lista_espera=lista_espera, titulo="Lista de consultas")

@app.route('/autenticar', methods=['POST'])
def autenticar():
    usuario = request.form.get('usuario')
    senha = request.form.get('senha')

    if not usuario or not senha:
        flash('Usuário e senha são obrigatórios!')
        return redirect(url_for('login'))

    if usuario == 'admin' and senha == 'admin':
        session['usuario_logado'] = usuario
        flash(f'{usuario}: Login realizado com sucesso!')
        return redirect(url_for('lista_pacientes'))

    flash('Usuário ou senha incorretos, tente novamente.')
    return redirect(url_for('login'))
@app.route('/cad-pac')
def cad_pac():
    return render_template('cadastro_paciente.html', titulo='Cadastro do paciente')


# Rota para cadastrar paciente (necessário ser POST para enviar dados do formulário)
@app.route('/cadastra', methods=['POST'])
def cadastradoPac():
    nome = request.form.get('nome')
    cpf = request.form.get('cpf')
    numero = request.form.get('num')
    email = request.form.get('email')
    nascimento = request.form.get('nasc')
    genero = request.form.get('sexo')
    abordagem = request.form.get('abordagem')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO pacientes (nome, cpf, numero, email, nascimento, genero, abordagem)
        VALUES (?, ?, ?, ?, ?, ?, ?)""", (nome, cpf, numero, email, nascimento, genero, abordagem))

    conn.commit()
    conn.close()

    flash('Paciente cadastrado com sucesso!')
    return redirect(url_for('lista_pacientes'))

# Rota para cadastrar psicólogo (necessário ser POST)
@app.route('/cadastrado', methods=['POST'])
def cadastradoPis():
    nome = request.form.get('nome')
    cpf = request.form.get('cpf')
    crp = request.form.get('crp')
    numero = request.form.get('numero')
    email = request.form.get('email')
    nasc = request.form.get('nasc')
    sexo = request.form.get('sexo')
    abordagem = request.form.get('abordagem')

    conn = get_db_connection()
    conn.execute("""
        INSERT INTO psicologos (nome, cpf, crp, numero, email, nasc, sexo, abordagem)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)""", (nome, cpf, crp, numero, email, nasc, sexo, abordagem))

    conn.commit()
    conn.close()

    flash('Piscólogo cadastrado com sucesso!')
    return redirect(url_for('lista_pacientes'))



@app.route('/cad-pis')
def cad_pis():
    return render_template('cadastro_psicologo.html', titulo='Cadastro do psicólogo')



@app.route('/login')
def login():
    proxima = request.args.get('proxima')
    return render_template('login.html', proxima=proxima)

@app.route('/logout')
def logout():
    session['usuario_logado'] = None
    flash('Logout realizado com sucesso')
    return redirect(url_for('lista_pacientes'))

@app.route('/pac-pis')
def pac_pis():
    # Conectando ao banco de dados
    conn = get_db_connection()

    # Buscando pacientes
    pacientes = conn.execute('SELECT id, nome FROM pacientes').fetchall()

    # Buscando psicólogos
    psicologos = conn.execute('SELECT id, nome FROM psicologos').fetchall()

    horarios = [f"{i:02}:00" for i in range(8, 21)]

    conn.close()

    # Renderizando o template e passando os pacientes e psicólogos
    return render_template('paciente_psicologo.html', pacientes=pacientes, psicologos=psicologos, horarios=horarios, titulo="Agendar consulta")


@app.route('/adicionar-lista-espera', methods=['POST'])
def adicionar_lista_espera():
    paciente_id = request.form.get('paciente_id')  # agora deve corresponder ao nome do campo
    psicologo_id = request.form.get('psicologo_id')  # agora deve corresponder ao nome do campo
    data = request.form.get('data')
    horario = request.form.get('horario')

    # Conectando ao banco de dados
    conn = get_db_connection()

    # Buscando o nome do paciente e psicólogo com base nos IDs selecionados
    paciente = conn.execute('SELECT nome FROM pacientes WHERE id = ?', (paciente_id,)).fetchone()
    psicologo = conn.execute('SELECT nome FROM psicologos WHERE id = ?', (psicologo_id,)).fetchone()

    # Verifique se ambos os registros foram encontrados
    if paciente is None:
        flash('Paciente não encontrado!')
        return redirect(url_for('pac_pis'))

    if psicologo is None:
        flash('Psicólogo não encontrado!')
        return redirect(url_for('pac_pis'))

    horario_ocupado = conn.execute("""
            SELECT * FROM lista_espera 
            WHERE psicologo_id = ? AND data = ? AND horario = ?
        """, (psicologo_id, data, horario)).fetchone()

    if horario_ocupado is not None:
        flash('Horário já ocupado, selecione um horário vago.')
        return redirect(url_for('pac_pis'))

    # Inserindo os dados na tabela lista_espera
    conn.execute("""
        INSERT INTO lista_espera (paciente_id, nome_paciente, psicologo_id, nome_psicologo, data, horario)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (paciente_id, paciente['nome'], psicologo_id, psicologo['nome'], data, horario))

    conn.commit()
    conn.close()

    flash('Paciente e Psicólogo adicionados à lista de espera com sucesso!')
    return redirect(url_for('pac_pis'))

@app.route('/consultas-marcadas')
def consultas_marcadas():

    conn = get_db_connection()

    lista_espera = conn.execute(""" SELECT id, horario, data, nome_paciente, nome_psicologo FROM lista_espera """).fetchall()

    conn.close()

    return render_template('lista_horarios.html', lista_espera=lista_espera, titulo="Lista de consultas")

app.run(debug=True)


