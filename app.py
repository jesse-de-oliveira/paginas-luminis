from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime, date

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', '3f9a8b2c1d4e7f')

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

from models import db, Usuario, Livro, StatusLeitura 
import models

db.init_app(app)

with app.app_context():
    db.create_all()

def current_user():
    if 'user_id' in session:
        return models.Usuario.query.get(session['user_id'])
    return None

@app.route('/')
def home():
    user = current_user()
    if user:
        livros = models.Livro.query.filter_by(usuario_id=user.id).all()
        desafios_pendentes = []
        uds = models.UsuarioDesafio.query.filter_by(usuario_id=user.id, concluido=False).all()
        todos_desafios = models.Desafio.query.all()
        ids_concluidos = {ud.desafio_id for ud in models.UsuarioDesafio.query.filter_by(usuario_id=user.id, concluido=True).all()}
        desafios_pendentes = [d for d in todos_desafios if d.id not in ids_concluidos]
        return render_template('index.html', user=user, livros=livros, hoje=date.today(), desafios_pendentes=desafios_pendentes)
    return render_template('home.html', user=None)

@app.route('/create_db')
def create_db():
    with app.app_context():
        db.create_all()
        return "DB criado."

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        senha = request.form['senha'].strip()
        if not username or not senha:
            return 'Preencha todos os campos!', 400
        if models.Usuario.query.filter_by(username=username).first():
            return 'Usuário já existe!', 400

        novo = models.Usuario(username=username, senha=generate_password_hash(senha))
        db.session.add(novo)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        senha = request.form['senha'].strip()
        user = models.Usuario.query.filter_by(username=username).first()
        if user and check_password_hash(user.senha, senha):
            session['user_id'] = user.id
            return redirect(url_for('home'))
        return 'Usuário ou senha incorretos!', 401
    return render_template('login.html')

@app.route('/logout')

def logout():
    session.pop('user_id', None)
    return redirect(url_for('home'))

@app.route('/conquistas')
def conquistas():
    user = current_user()
    if not user:
        return redirect(url_for('login'))
    
    conquistas_usuario = models.UsuarioConquista.query.filter_by(usuario_id=user.id).all()
    return render_template('conquistas.html', conquistas=conquistas_usuario, user=user)

# --------------------- LIVROS ---------------------
@app.route('/livros')
def listar_livros():
    user = current_user()
    if not user:
        return redirect(url_for('login'))
    livros = models.Livro.query.filter_by(usuario_id=user.id).all()
    return render_template('livros.html', livros=livros, user=user)


@app.route('/livros/add', methods=['POST'])
def add_livro():
    user = current_user()
    if not user:
        return redirect(url_for('login'))
    titulo = request.form['titulo'].strip()
    autor = request.form['autor'].strip()
    paginas = request.form.get('total_paginas', '').strip()
    total_paginas = int(paginas) if paginas.isdigit() else None

    if models.Livro.query.filter_by(usuario_id=user.id, titulo=titulo, autor=autor).first():
        return 'Este livro já está cadastrado!', 400

    novo = models.Livro(
        titulo=titulo,
        autor=autor,
        total_paginas=total_paginas,
        status=models.StatusLeitura.QUERO_LER,
        usuario_id=user.id
    )
    db.session.add(novo)
    db.session.commit()
    return redirect(url_for('listar_livros'))


@app.route('/livros/<int:livro_id>/status', methods=['POST'])
def mudar_status(livro_id):
    user = current_user()
    if not user:
        return redirect(url_for('login'))
    livro = models.Livro.query.get_or_404(livro_id)
    if livro.usuario_id != user.id:
        return 'Proibido', 403

    novo_status_texto = request.form['status']
    livro.status = models.StatusLeitura(novo_status_texto)
    db.session.commit()
    return redirect(url_for('listar_livros'))

# ==================== REGISTRO DE LEITURA + PROGRESSO ====================== #

@app.route('/livro/<int:livro_id>')
def ver_livro(livro_id):
    user = current_user()
    if not user:
        return redirect(url_for('login'))

    livro = models.Livro.query.get_or_404(livro_id)
    if livro.usuario_id != user.id:
        return 'Acesso negado!', 403

    # Todas as leituras deste livro
    leituras = models.Leitura.query.filter_by(livro_id=livro_id).order_by(models.Leitura.data.desc()).all()

    # Calcula total de páginas lidas
    total_lido = sum(leitura.paginas_lidas or 0 for leitura in leituras)
    progresso = (total_lido / livro.total_paginas * 100) if livro.total_paginas else 0
    progresso = min(100, round(progresso, 1))

    # Atualiza status automaticamente se completou o livro
    if livro.total_paginas and total_lido >= livro.total_paginas:
        if livro.status != models.StatusLeitura.JA_LIDO:
            livro.status = models.StatusLeitura.JA_LIDO
            db.session.commit()

    return render_template('ver_livro.html',
                           livro=livro,
                           leituras=leituras,
                           progresso=progresso,
                           total_lido=total_lido, user=user)


@app.route('/livro/<int:livro_id>/ler', methods=['POST'])
def registrar_leitura(livro_id):
    user = current_user()
    if not user:
        return redirect(url_for('login'))

    livro = models.Livro.query.get_or_404(livro_id)
    if livro.usuario_id != user.id:
        return 'Acesso negado!', 403

    paginas = request.form.get('paginas_lidas', '').strip()
    if not paginas.isdigit() or int(paginas) <= 0:
        return 'Digite um número válido!', 400
    paginas = int(paginas)

    
    nova = models.Leitura(paginas_lidas=paginas, livro_id=livro_id, usuario_id=user.id)
    db.session.add(nova)
    db.session.flush()  

    
    if livro.status == models.StatusLeitura.QUERO_LER:
        livro.status = models.StatusLeitura.EM_ANDAMENTO

    
    total_lido = sum(l.paginas_lidas or 0 for l in livro.leituras)

    completou_agora = False
    if livro.total_paginas and total_lido >= livro.total_paginas:
        if livro.status != models.StatusLeitura.JA_LIDO:
            livro.status = models.StatusLeitura.JA_LIDO
            completou_agora = True

    db.session.commit()

    
    if completou_agora:
        conquista_nome = "Primeiro Livro Concluído"
        conquista = models.Conquista.query.filter_by(nome=conquista_nome).first()
        if not conquista:
            conquista = models.Conquista(nome=conquista_nome, descricao="Terminou de ler seu primeiro livro!")
            db.session.add(conquista)
            db.session.commit()

        if not models.UsuarioConquista.query.filter_by(usuario_id=user.id, conquista_id=conquista.id).first():
            db.session.add(models.UsuarioConquista(usuario_id=user.id, conquista_id=conquista.id))
            db.session.commit()

    return redirect(url_for('ver_livro', livro_id=livro_id))
    

# ====================== DIÁRIO DE LEITURA ======================
@app.route('/diario')
def diario():
    user = current_user()
    if not user:
        return redirect(url_for('login'))
    entradas = models.Diario.query.filter_by(usuario_id=user.id)\
                                 .order_by(models.Diario.data.desc()).all()
    return render_template('diario.html', entradas=entradas, user=user)

@app.route('/diario/novo', methods=['GET', 'POST'])
def novo_diario():
    user = current_user()
    if not user:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        livro_id = request.form.get('livro_id') or None
        novo = models.Diario(
            titulo=request.form['titulo'],
            conteudo=request.form['conteudo'],
            tipo=models.TipoDiario(request.form['tipo']),
            livro_id=int(livro_id) if livro_id else None,
            usuario_id=user.id
        )
        db.session.add(novo)
        db.session.commit()
        return redirect(url_for('diario'))

    livros = models.Livro.query.filter_by(usuario_id=user.id).all()
    return render_template('novo_diario.html', livros=livros, user=user)

# ====================== FRASES FAVORITAS ======================
@app.route('/frases')
def listar_frases():
    user = current_user()
    if not user:
        return redirect(url_for('login'))
    frases = models.FraseFavorita.query.filter_by(usuario_id=user.id).all()
    livros = models.Livro.query.filter_by(usuario_id=user.id).all()
    return render_template('frases.html', frases=frases, livros=livros, user=user)

@app.route('/frases/add', methods=['POST'])
def add_frase():
    user = current_user()
    if not user:
        return redirect(url_for('login'))
    texto = request.form['texto'].strip()
    livro_id = request.form['livro_id']
    nome_autor = request.form.get('nome_autor', '').strip()
    pagina = request.form.get('pagina', '').strip()
    if not texto:
        return redirect(url_for('listar_frases'))
    nova = models.FraseFavorita(
        texto=texto,
        nome_autor=nome_autor or None,
        pagina=int(pagina) if pagina.isdigit() else None,
        livro_id=livro_id,
        usuario_id=user.id
    )
    db.session.add(nova)
    db.session.commit()
    return redirect(url_for('listar_frases'))


# ====================== DESAFIOS ======================
@app.route('/desafios')
def listar_desafios():
    user = current_user()
    if not user:
        return redirect(url_for('login'))
    # Cria desafios padrão se não existirem
    desafios_padrao = [
        ('Leia por 20 minutos hoje', 'diario'),
        ('Leia antes de dormir', 'diario'),
        ('Leia 5 páginas hoje', 'diario'),
        ('Escreva uma reflexão no diário', 'semanal'),
        ('Adicione uma frase favorita', 'semanal'),
        ('Termine um capítulo hoje', 'diario'),
    ]
    for descricao, tipo in desafios_padrao:
        if not models.Desafio.query.filter_by(descricao=descricao).first():
            db.session.add(models.Desafio(
                descricao=descricao,
                tipo=models.TipoDesafio(tipo)
            ))
    db.session.commit()

    todos = models.Desafio.query.all()
    usuario_desafios = {
        ud.desafio_id: ud
        for ud in models.UsuarioDesafio.query.filter_by(usuario_id=user.id).all()
    }
    return render_template('desafios.html', desafios=todos, usuario_desafios=usuario_desafios, user=user)

@app.route('/desafios/<int:desafio_id>/concluir', methods=['POST'])
def concluir_desafio(desafio_id):
    user = current_user()
    if not user:
        return redirect(url_for('login'))
    ud = models.UsuarioDesafio.query.filter_by(
        usuario_id=user.id, desafio_id=desafio_id
    ).first()
    if ud:
        ud.concluido = not ud.concluido
    else:
        ud = models.UsuarioDesafio(
            usuario_id=user.id,
            desafio_id=desafio_id,
            concluido=True
        )
        db.session.add(ud)
    db.session.commit()
    return redirect(url_for('listar_desafios'))

if __name__ == '__main__': 
    app.run(debug=True)