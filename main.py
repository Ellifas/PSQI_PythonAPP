from flask import Flask, render_template, request, redirect, url_for, session, logging
import json
import os
from datetime import datetime
from functools import wraps
import plotly.graph_objs as go
import plotly.offline as pyo


app = Flask(__name__)
app.secret_key = 'supersecretkey'

USERS_FILE = 'users.json'
PROFILE_FILE = 'profile_data.json'

def load_json(filename, default_data):
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                return default_data
    else:
        return default_data

def save_json(filename, data):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)

# Carregar dados
users = load_json(USERS_FILE, {})
profile_data = load_json(PROFILE_FILE, {})

def login_required(f):
    @wraps(f)  
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Função que gera a explicação com base na pontuação
def gerar_explicacao_psqi(pontuacao_total):
    if pontuacao_total > 5:
        return "Uma pontuação acima de 5 indica que a qualidade do sono é insatisfatória, sugerindo problemas que podem afetar a saúde."
    elif pontuacao_total <= 5:
        return "Uma pontuação igual ou abaixo de 5 indica que a qualidade do sono é satisfatória."
    else:
        return "Pontuação não disponível."

@app.route('/')
def home():
    username = session.get('username')
    return render_template('home.html', username=username)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if email in users and users[email]['password'] == password:
            session['username'] = email
            return redirect(url_for('home'))
        else:
            return "E-mail ou senha incorretos"
    return render_template('login.html')

@app.route('/cadastrar', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        if password == confirm_password:
            users[email] = {'name': name, 'password': password}
            profile_data[email] = {'name': name, 'email': email, 'form_data': []}
            save_json(USERS_FILE, users)
            save_json(PROFILE_FILE, profile_data)
            return redirect(url_for('login'))
        else:
            return "Senhas não conferem"
    return render_template('cadastrar.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

@app.route('/perfil')
@login_required
def user_profile():
    username = session.get('username')
    if username not in profile_data:
        return "Nenhum dado encontrado para o usuário.", 404
    
    user_profile = profile_data[username]

    if user_profile['form_data']:
        dados_recente = user_profile['form_data'][-1]
        total_score = dados_recente.get('total_score', 0)
    else:
        total_score = 0

    explicacao = gerar_explicacao_psqi(total_score)
    
    return render_template('user_profile.html', 
                           user_profile=user_profile,
                           psqi_score=total_score, 
                           explanation=explicacao)

@app.route('/formulario', methods=['GET', 'POST'])
@login_required
def formulario():
    username = session.get('username')

    if request.method == 'POST':
        try:
            hora_deitar = request.form.get('hora-deitar')
            hora_levantar = request.form.get('hora-levantar')
            horas_de_sono = request.form.get('horas-de-sono', '0')
            questao6 = int(request.form.get('questao6', '0'))
            questao7 = int(request.form.get('questao7', '0'))
            questao8 = int(request.form.get('questao8', '0'))
            questao9 = int(request.form.get('questao9', '0'))

            if not hora_deitar or not hora_levantar:
                raise ValueError("Os horários de deitar e levantar são obrigatórios.")

            total_score = calcular_pontuacao(hora_deitar, hora_levantar, horas_de_sono, questao6, questao7, questao8, questao9)

            participant_data = {
                'username': username,
                'hora_deitar': hora_deitar,
                'hora_levantar': hora_levantar,
                'horas_de_sono': horas_de_sono,
                'total_score': total_score,
                'questao6': questao6,
                'data': datetime.now().strftime('%Y-%m-%d')
            }

            profile_data[username]['form_data'].append(participant_data)
            save_json(PROFILE_FILE, profile_data)

            return redirect(url_for('historico'))

        except Exception as e:
            logging.error(f"Erro ao processar o formulário: {e}")
            return "Ocorreu um erro ao processar o formulário.", 500

    return render_template('formulario.html')

def calcular_pontuacao(hora_deitar, hora_levantar, horas_de_sono, questao6, questao7, questao8, questao9):
    score1 = questao6
    score2 = int(horas_de_sono)
    return score1 + score2

@app.route('/historico', methods=['GET'])
@login_required
def historico():
    username = session.get('username')
    if username not in profile_data:
        return "Nenhum dado encontrado para o usuário.", 404

    user_profile = profile_data[username]
    scores = []

    for entry in user_profile['form_data']:
        data = entry.get('data', 'Data indisponível')
        try:
            data_formatada = datetime.strptime(data, '%Y-%m-%d').strftime('%d/%m/%Y')
        except ValueError:
            data_formatada = data

        total_score = entry.get('total_score', 0)
        questao6 = entry.get('questao6', None)

        scores.append({
            'data': data_formatada,
            'total_score': total_score,
            'questao6': questao6
        })

    gerar_grafico_historico(scores)

    return render_template('historico.html', scores=scores, username=username)

def gerar_grafico_historico(scores):
    datas = [entry['data'] for entry in scores]
    pontuacoes = [entry['total_score'] for entry in scores]

    trace = go.Scatter(
        x=datas,
        y=pontuacoes,
        mode='lines+markers',
        name='Pontuação do Sono'
    )
    layout = go.Layout(
        title='Histórico de Pontuação do Sono',
        xaxis=dict(title='Data'),
        yaxis=dict(title='Pontuação Total')
    )
    fig = go.Figure(data=[trace], layout=layout)
    pyo.plot(fig, filename='static/historico_sono.html', auto_open=False)

if __name__ == "__main__":
    app.run(debug=True)
