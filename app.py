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
    return render_template('lista_horarios.html', titulo='Lista de pacientes')

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
def cadastradoPas():
    nome = request.form.get('nome_pac')
    cpf = request.form.get('cpf_pac')
    numero = request.form.get('num_pac')
    email = request.form.get('email_pac')
    nascimento = request.form.get('nasc_pac')
    genero = request.form.get('sexo_pac')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO pacientes (nome, cpf, numero, email, nascimento, genero)
        VALUES (?, ?, ?, ?, ?, ?)""", (nome, cpf, numero, email, nascimento, genero))

    conn.commit()
    conn.close()

    flash('Pasciente cadastrado com sucesso!')
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

    conn = get_db_connection()
    conn.execute("""
        INSERT INTO psicologos (nome, cpf, crp, numero, email, nasc, sexo)
        VALUES (?, ?, ?, ?, ?, ?, ?)""", (nome, cpf, crp, numero, email, nasc, sexo))

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

    conn.close()

    # Renderizando o template e passando os pacientes e psicólogos
    return render_template('paciente_psicologo.html', pacientes=pacientes, psicologos=psicologos, titulo="Agendar consulta")


@app.route('/adicionar-lista-espera', methods=['POST'])
def adicionar_lista_espera():
    paciente_id = request.form.get('paciente_id')  # agora deve corresponder ao nome do campo
    psicologo_id = request.form.get('psicologo_id')  # agora deve corresponder ao nome do campo

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

    # Inserindo os dados na tabela lista_espera
    conn.execute("""
        INSERT INTO lista_espera (paciente_id, nome_paciente, psicologo_id, nome_psicologo)
        VALUES (?, ?, ?, ?)
    """, (paciente_id, paciente['nome'], psicologo_id, psicologo['nome']))

    conn.commit()
    conn.close()

    flash('Paciente e Psicólogo adicionados à lista de espera com sucesso!')
    return redirect(url_for('pac_pis'))


app.run(debug=True)


