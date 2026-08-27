# 📚 Páginas Luminis

A proposta deste projeto é a criação de um website interativo que incentive o hábito da leitura, especialmente entre quem ainda não lê com frequência. A ideia é oferecer ferramentas que tornem a leitura uma experiência mais envolvente, estimulante e contínua.

🔗 **Aplicação ao vivo:** https://paginas-luminis.onrender.com/
📄 **Documentação e diagramas:** https://jesse-de-oliveira.github.io/paginas-luminis/

## Funcionalidades

- 📘 Desafios de Leitura
- 📓 Diário de Leitura / Resumo
- 📖 Frases Favoritas
- 📊 Tracker de Leitura
- 🏅 Sistema de Conquistas

## Tecnologias utilizadas

- Python 3, Flask, SQLAlchemy, SQLite (local), PostgreSQL (produção), JavaScript, Jinja2, Gunicorn

## Como rodar localmente

### Pré-requisitos
- Python 3.10+ instalado

### Passos

1. Clone o repositório:

git clone https://github.com/jesse-de-oliveira/paginas-luminis.git
cd paginas-luminis

2. Crie e ative o ambiente virtual:

python -m venv venv
venv\Scripts\activate

3. Instale as dependências:

pip install -r requirements.txt

4. Rode a aplicação:

python app.py

5. Acesse no navegador:

http://127.0.0.1:5000

## Como rodar os testes

pytest tests/test_app.py -v

## Estrutura do banco de dados

Veja os diagramas completos (casos de uso, classes, DER) em:
https://jesse-de-oliveira.github.io/paginas-luminis/