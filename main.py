from flask import Flask, render_template, request, redirect, url_for, session # type: ignore
import json
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Arquivos JSON
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
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

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
            profile_data[email] = {'name': name, 'email': email, 'form_data': {}}
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

@app.route('/formulario', methods=['GET', 'POST'])
def formulario():
    username = session.get('username')
    
    # Verifica se o usuário está logado
    if not username:
        return redirect(url_for('login'))  # Redireciona para a página de login se não estiver logado

    if request.method == 'POST':
        try:
            # Coleta de dados do formulário
            participant_data = {
                'nome': request.form.get('nome', ''),
                'id': request.form.get('id', ''),
                'data_nascimento': request.form.get('data-nascimento', ''),
                'hora_deitar': request.form.get('hora-deitar', ''),
                'tempo_para_dormir': request.form.get('tempo-para-dormir', ''),
                'hora_levantar': request.form.get('hora-levantar', ''),
                'horas_de_sono': request.form.get('horas-de-sono', ''),
                'questao5a': int(request.form.get('questao5a', 0)),
                'questao5b': int(request.form.get('questao5b', 0)),
                'questao5c': int(request.form.get('questao5c', 0)),
                'questao5d': int(request.form.get('questao5d', 0)),
                'questao5e': int(request.form.get('questao5e', 0)),
                'questao5f': int(request.form.get('questao5f', 0)),
                'questao5g': int(request.form.get('questao5g', 0)),
                'questao5h': int(request.form.get('questao5h', 0)),
                'questao5i': int(request.form.get('questao5i', 0)),
                'questao5j': int(request.form.get('questao5j', 0)),
                'questao6': int(request.form.get('qualidade-do-sono', 0)),
                'questao7': int(request.form.get('uso-medicamento', 0)),
                'questao8': int(request.form.get('dificuldade-acordado', 0)),
                'questao9': int(request.form.get('manter-animacao', 0)),
                'questao10': int(request.form.get('parceiro', 0))
            }
            
            # Cálculo da pontuação do PSQI
            latency_score = calcular_latencia(int(request.form.get('questao2', 0)))
            disturbances_component_score = calcular_disturbios(participant_data['questao5a'])
            efficiency_score = calcular_eficiencia(participant_data['horas_de_sono'], 
                                                     request.form.get('hora_deitar', 0), 
                                                     request.form.get('hora_levantar', 0))

            total_score = (
                participant_data['questao6'] +
                participant_data['questao7'] +
                participant_data['questao8'] +
                participant_data['questao9'] +
                participant_data['questao10'] +
                latency_score +
                disturbances_component_score +
                efficiency_score
            )
            
            # Atualiza os dados do formulário no perfil do usuário
            if username in profile_data:
                user_profile = profile_data[username]
                user_profile['form_data'].append(participant_data)
                user_profile['psqi_scores'].append(total_score)
                save_json(PROFILE_FILE, profile_data)

            return redirect(url_for('home'))
        except Exception as e:
            print(f"Erro ao processar o formulário: {e}")
            return "Ocorreu um erro ao processar o formulário.", 500

def calcular_latencia(score):
    if score <= 15:
        return 0
    elif 16 <= score <= 30:
        return 1
    elif 31 <= score <= 60:
        return 2
    else:
        return 3

def calcular_disturbios(score):
    if score <= 0:
        return 0
    elif 1 <= score <= 9:
        return 1
    elif 10 <= score <= 18:
        return 2
    else:
        return 3

def calcular_eficiencia(horas_de_sono, hora_deitar, hora_levantar):
    sleep_hours = float(horas_de_sono)
    total_hours_in_bed = (
        int(hora_levantar) - int(hora_deitar)
    )
    sleep_efficiency = (sleep_hours / total_hours_in_bed) * 100 if total_hours_in_bed > 0 else 0
    
    if sleep_efficiency > 85:
        return 0
    elif 75 <= sleep_efficiency <= 84:
        return 1
    elif 65 <= sleep_efficiency <= 74:
        return 2
    else:
        return 3

    return render_template('formulario.html')


@app.route('/perfil', methods=['GET', 'POST'])
@login_required
def perfil():
    username = session.get('username')
    user_profile = profile_data.get(username, {'name': '', 'email': '', 'form_data': {}, 'psqi_score': 0})

    if request.method == 'POST':
        # Certifique-se de que 'name' e outras variáveis estão corretamente definidas
        name = request.form.get('name', '')  # Ou qualquer outro método para obter 'name'
        profile_data[username] = {
            'name': name,
            'email': request.form.get('email', ''),
            'form_data': user_profile.get('form_data', {}),
            'psqi_score': user_profile.get('psqi_score', 0)
        }
        save_json(PROFILE_FILE, profile_data)
        return redirect(url_for('perfil'))

    # Explicação do PSQI
    score = user_profile.get('psqi_score', 0)
    explanation = ""
    if score > 5:
        explanation = "Sua pontuação no PSQI indica possíveis problemas com a qualidade do sono. Considere consultar um especialista."
    else:
        explanation = "Sua pontuação no PSQI sugere uma boa qualidade do sono."

    return render_template('user_profile.html', user_profile=user_profile, explanation=explanation)


def calcular_psqi(form_data):
    # Pontuação por componente
    pontuacoes = {
        'componente1': 0,
        'componente2': 0,
        'componente3': 0,
        'componente4': 0,
        'componente5': 0,
        'componente6': 0,
        'componente7': 0
    }
    
    # Componente 1: Qualidade subjetiva do sono
    pontuacoes['componente1'] = int(form_data.get('questao6', 0))
    
    # Componente 2: Latência do sono
    latencia = int(form_data.get('questao2', 0))
    if latencia <= 15:
        pontuacoes['componente2'] = 0
    elif latencia <= 30:
        pontuacoes['componente2'] = 1
    elif latencia <= 60:
        pontuacoes['componente2'] = 2
    else:
        pontuacoes['componente2'] = 3

    # Pontuação adicional para a questão 5a
    questao5a = int(form_data.get('questao5a', 0))
    if questao5a == 0:
        pontuacoes['componente2'] += 0
    elif questao5a <= 1:
        pontuacoes['componente2'] += 1
    elif questao5a <= 2:
        pontuacoes['componente2'] += 2
    elif questao5a <= 3:
        pontuacoes['componente2'] += 3

    # Ajustar a pontuação do componente 2
    if pontuacoes['componente2'] > 3:
        pontuacoes['componente2'] = 3

    # Componente 3: Duração do sono
    duracao_sono = int(form_data.get('questao4', 0))
    if duracao_sono > 7:
        pontuacoes['componente3'] = 0
    elif duracao_sono >= 6:
        pontuacoes['componente3'] = 1
    elif duracao_sono >= 5:
        pontuacoes['componente3'] = 2
    else:
        pontuacoes['componente3'] = 3

    # Componente 4: Eficiência habitual do sono
    horas_dormidas = float(form_data.get('horas_dormidas', 0))
    horario_deitar = float(form_data.get('hora_deitar', 0))
    horario_levantar = float(form_data.get('hora_levantar', 0))
    horas_no_leito = horario_levantar - horario_deitar
    eficiencia_sono = (horas_dormidas / horas_no_leito) * 100
    if eficiencia_sono > 85:
        pontuacoes['componente4'] = 0
    elif eficiencia_sono >= 75:
        pontuacoes['componente4'] = 1
    elif eficiencia_sono >= 65:
        pontuacoes['componente4'] = 2
    else:
        pontuacoes['componente4'] = 3

    # Componente 5: Distúrbios do sono
    disturios = [
        int(form_data.get('questao5b', 0)),
        int(form_data.get('questao5c', 0)),
        int(form_data.get('questao5d', 0)),
        int(form_data.get('questao5e', 0)),
        int(form_data.get('questao5f', 0)),
        int(form_data.get('questao5g', 0)),
        int(form_data.get('questao5h', 0)),
        int(form_data.get('questao5i', 0)),
        int(form_data.get('questao5j', 0))
    ]
    total_disturios = sum(disturios)
    if total_disturios == 0:
        pontuacoes['componente5'] = 0
    elif total_disturios <= 9:
        pontuacoes['componente5'] = 1
    elif total_disturios <= 18:
        pontuacoes['componente5'] = 2
    else:
        pontuacoes['componente5'] = 3

    # Componente 6: Uso de remédio para dormir
    pontuacoes['componente6'] = int(form_data.get('questao7', 0))

    # Componente 7: Disfunção diurna
    disfuncao_diurna = int(form_data.get('questao8', 0)) + int(form_data.get('questao9', 0))
    if disfuncao_diurna == 0:
        pontuacoes['componente7'] = 0
    elif disfuncao_diurna <= 2:
        pontuacoes['componente7'] = 1
    elif disfuncao_diurna <= 4:
        pontuacoes['componente7'] = 2
    else:
        pontuacoes['componente7'] = 3

    # Pontuação global
    pontuacao_total = sum(pontuacoes.values())
    
    return pontuacao_total

@app.route('/historico')
def historico():
    username = session.get('username', 'user1')  # Valor padrão para testes
    user_profile = profile_data.get(username, {'form_data': {}, 'psqi_scores': []})

    # Calcular a pontuação do PSQI
    psqi_score = calcular_psqi(user_profile['form_data'])
    user_profile['psqi_scores'].append(psqi_score)

    return render_template('historico.html', form_data=user_profile['form_data'], psqi_scores=user_profile['psqi_scores'], psqi_score=psqi_score)



if __name__ == '__main__':
    app.run(debug=True)


