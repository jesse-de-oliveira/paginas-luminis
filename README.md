# 📚 Páginas Luminis

Website interativo para incentivar o hábito da leitura. O usuário organiza seus livros, registra o progresso de leitura, escreve um diário, guarda frases favoritas, cumpre desafios e ganha conquistas.

Projeto de extensão do curso de Engenharia de Software (EaD) da UniFil, desenvolvido por **Jesse de Oliveira** e **Vincenzo Izzo**.

| | |
|---|---|
| 🔗 Aplicação ao vivo | https://paginas-luminis.onrender.com/ |
| 📄 Portfólio e documentação | https://jesse-de-oliveira.github.io/paginas-luminis/ |
| 💻 Código-fonte | https://github.com/jesse-de-oliveira/paginas-luminis |

> ⏳ **Aviso:** a aplicação roda em planos gratuitos de hospedagem. Se ninguém a acessou há alguns minutos, a primeira visita pode demorar cerca de 1 minuto ou mostrar o erro **502 Bad Gateway**. É normal: aguarde alguns segundos e **recarregue a página (F5)**.

## O problema

Segundo a pesquisa Retratos da Leitura no Brasil (2024), o país perdeu 6,7 milhões de leitores em quatro anos, e pela primeira vez a maioria da população (53%) não leu nem parte de um livro nos três meses anteriores à pesquisa. O Páginas Luminis propõe uma forma leve e motivadora de criar ou retomar o hábito de ler.

## Funcionalidades

| Funcionalidade | Descrição |
|---|---|
| 🏠 Dashboard | Páginas lidas hoje, livros em andamento e desafios pendentes |
| 📚 Tracker de leitura | Livros organizados em Quero Ler, Em Andamento e Já Lido, com progresso por páginas |
| 📓 Diário de leitura | Resumos, reflexões e comentários, com leitura de cada entrada |
| 💬 Frases favoritas | Trechos marcantes salvos por livro |
| 🎯 Desafios | Desafios diários e semanais que podem ser marcados como concluídos |
| 🏆 Conquistas | Recompensas leves para reforçar a motivação |

![Dashboard](docs/imagens/dashboard.png)
![Tracker de leitura](docs/imagens/tracker.png)
![Registro de leitura](docs/imagens/registrar-leitura.png)

## Tecnologias

- Python 3, Flask, Flask-SQLAlchemy, Jinja2, JavaScript
- SQLite (desenvolvimento local) e PostgreSQL (produção, Neon)
- Gunicorn e Render (hospedagem)
- pytest (testes automatizados)

## Estrutura do projeto

```
paginas-luminis/
├── app.py              # rotas e lógica da aplicação
├── models.py           # modelos do banco de dados
├── requirements.txt    # dependências
├── static/             # CSS e JavaScript
├── templates/          # páginas HTML (Jinja2)
├── tests/test_app.py   # testes automatizados
└── docs/               # página do GitHub Pages e diagramas
```

## Como rodar localmente

Pré-requisito: Python 3.10 ou superior.

1. Clone o repositório:
   ```
   git clone https://github.com/jesse-de-oliveira/paginas-luminis.git
   cd paginas-luminis
   ```
2. Crie e ative o ambiente virtual:
   ```
   python -m venv venv
   venv\Scripts\activate
   ```
   No Linux ou macOS: `source venv/bin/activate`
3. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```
4. Rode a aplicação:
   ```
   python app.py
   ```
5. Acesse http://127.0.0.1:5000

Localmente não é preciso configurar nada: sem variáveis de ambiente, a aplicação usa um banco SQLite (`database.db`), criado automaticamente.

## Testes

```
pytest tests/test_app.py -v
```

São 9 testes que cobrem cadastro, login, adição e listagem de livros e registro de leitura (incluindo a conclusão automática do livro e a validação de entradas inválidas). Eles usam um banco SQLite em memória, sem afetar os dados reais.

## Deploy

A aplicação está publicada no Render (Web Service) com banco PostgreSQL no Neon.

- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn app:app`
- Variáveis de ambiente:
  - `SECRET_KEY`: chave secreta das sessões do Flask
  - `DATABASE_URL`: string de conexão do PostgreSQL, no formato `postgresql+psycopg2://usuario:senha@host/banco?sslmode=require`

## Diagramas

Casos de uso, diagrama de classes e DER estão no portfólio:
https://jesse-de-oliveira.github.io/paginas-luminis/

## Autores

Jesse de Oliveira e Vincenzo Izzo