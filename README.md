# Projeto de Qualidade do Sono

Este projeto é uma aplicação web desenvolvida em Flask para coletar e analisar dados sobre a qualidade do sono dos usuários. A aplicação permite que os usuários se cadastrem, façam login, preencham um questionário sobre sono e visualizem um histórico de suas pontuações.

## Pré-requisitos

Antes de começar, você precisará ter o seguinte instalado em sua máquina:

- Python 3.x
- pip (gerenciador de pacotes do Python)

## Instalação

Siga as etapas abaixo para configurar e executar a aplicação:

### 1. Clone o repositório

```bash
git clone https://github.com/seu_usuario/nome_do_repositorio.git
cd nome_do_repositorio

2. Crie um ambiente virtual
É uma boa prática usar um ambiente virtual para isolar suas dependências. Para criar um ambiente virtual, execute os seguintes comandos:

# No Windows
python -m venv venv

# No macOS/Linux
python3 -m venv venv

3. Ative o ambiente virtual
Ative o ambiente virtual com um dos seguintes comandos:

# No Windows
venv\Scripts\activate

# No macOS/Linux
source venv/bin/activate

4. Instale as dependências
Instale as dependências necessárias usando o pip.
Flask==2.0.3
plotly==5.3.1

pip install flask
pip install plotly

5. Execute a aplicação
Após instalar as dependências, você pode executar a aplicação com o seguinte comando:

# No Windows
set FLASK_APP=app.py
set FLASK_ENV=development
flask run

# No macOS/Linux
export FLASK_APP=app.py
export FLASK_ENV=development
flask run

6. Acesse a aplicação

Abra seu navegador e acesse http://127.0.0.1:5000. Você verá a página inicial da aplicação. 

Estrutura do Projeto

app.py: O arquivo principal da aplicação Flask.
templates/: Pasta contendo os arquivos HTML.
static/: Pasta para arquivos estáticos (CSS, JavaScript, etc.).
users.json: Armazena informações dos usuários.
profile_data.json: Armazena os dados dos formulários preenchidos.

Contribuição
Se você quiser contribuir para este projeto, fique à vontade para abrir um problema (issue) ou fazer um pull request.
