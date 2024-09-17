from flask import Flask, render_template, redirect

app = Flask(__name__)
app.config['SECRET_KEY'] = "TESTE"
if __name__ == '__main__':
    app.run(debug=True)

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/informacoes')
def informacoes():
    return render_template('info.html')

@app.route('/logado')
def entrar():
    nome = request.form.get('nome')
    senha = request.form.get('senha')
    return render_template("logado")

# deixar o site hospedado no heroku
# definir usuario por nome 
#