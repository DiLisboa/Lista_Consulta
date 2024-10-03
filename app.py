from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def lista_pacientes():
    return render_template('lista_horarios.html', titulo='Lista de pacientes')

@app.route('/cad-pac')
def cad_pac():
    return render_template('cadastro_paciente.html', titulo='Cadastro do paciente')

@app.route('/cad-pis')
def cad_pis():
    return render_template('cadastro_psicologo.html', titulo='Cadastro do piscologo')

@app.route('/login')
def login():
    return render_template('login.html')


app.run(debug=True)
