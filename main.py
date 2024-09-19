from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Mude isso para uma chave secreta real

# Usuários fictícios para exemplo
users = {
    "user@example.com": "password123"
}

@app.route('/')
def home():
    username = session.get('username')
    return render_template('home.html', username=username)

@app.route('/informacoes')
def informacoes():
    return render_template('informacoes.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if email in users and users[email] == password:
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
            users[email] = password
            return redirect(url_for('login'))
        else:
            return "Senhas não conferem"
    return render_template('cadastrar.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
