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
    nome = request.form.get('nome')
    cpf = request.form.get('cpf')
    numero = request.form.get('numero')
    email = request.form.get('email')
    nascimento = request.form.get('nasc')
    genero = request.form.get('sexo')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO pacientes (nome, cpf, numero, email, nascimento, genero)
        VALUES (?, ?, ?, ?, ?, ?)""", (nome, cpf, numero, email, nascimento, genero))

    conn.commit()
    conn.close()

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


app.run(debug=True)
