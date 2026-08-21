import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app as flask_app
from models import db, Usuario, StatusLeitura, Livro

@pytest.fixture
def app():
    flask_app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"
    })

    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.drop_all()


@pytest.fixture 
def client(app):
    return app.test_client()

def test_register_success(client):
    response = client.post('/register', data={
        'username': 'jesse',
        'senha': '123456'
    })
    assert response.status_code == 302  # redirect pro login = sucesso


def test_register_duplicate_user(client, app):
    with app.app_context():
        db.session.add(Usuario(username='jesse', senha='hash-fake'))
        db.session.commit()

    response = client.post('/register', data={
        'username': 'jesse',
        'senha': '123456'
    })
    assert response.status_code == 400  # já existe = erro


def test_login_success(client):
    client.post('/register', data={'username': 'jesse', 'senha': '123456'})
    response = client.post('/login', data={'username': 'jesse', 'senha': '123456'})
    assert response.status_code == 302  # login certo = redirect pra home

def test_add_livro_success(client):
    client.post('/register', data={'username': 'jesse', 'senha': '123456'})
    client.post('/login', data={'username': 'jesse', 'senha': '123456'})

    response = client.post('/livros/add', data={
        'titulo': 'Dom Casmurro',
        'autor': 'Machado de Assis',
        'total_paginas': '256'
    })
    assert response.status_code == 302  # redirect pra listagem = sucesso


def test_add_livro_duplicado(client):
    client.post('/register', data={'username': 'jesse', 'senha': '123456'})
    client.post('/login', data={'username': 'jesse', 'senha': '123456'})

    client.post('/livros/add', data={
        'titulo': 'Dom Casmurro',
        'autor': 'Machado de Assis',
        'total_paginas': '256'
    })
    response = client.post('/livros/add', data={
        'titulo': 'Dom Casmurro',
        'autor': 'Machado de Assis',
        'total_paginas': '256'
    })
    assert response.status_code == 400  # já existe = erro


def test_listar_livros(client):
    client.post('/register', data={'username': 'jesse', 'senha': '123456'})
    client.post('/login', data={'username': 'jesse', 'senha': '123456'})
    client.post('/livros/add', data={
        'titulo': 'Dom Casmurro',
        'autor': 'Machado de Assis',
        'total_paginas': '256'
    })

    response = client.get('/livros')
    assert response.status_code == 200
    assert b'Dom Casmurro' in response.data  # verifica se o titulo aparece na pagina

def test_registrar_leitura_success(client):
    client.post('/register', data={'username': 'vincenzo', 'senha': '123456'})
    client.post('/login', data={'username': 'vincenzo', 'senha': '123456'})
    client.post('/livros/add', data={
        'titulo': 'O Cortiço',
        'autor': 'Aluísio Azevedo',
        'total_paginas': '200'
    })

    # pega o id do livro recem criado direto do banco
    livro = Livro.query.filter_by(titulo='O Cortiço').first()

    response = client.post(f'/livro/{livro.id}/ler', data={
        'paginas_lidas': '50'
    })
    assert response.status_code == 302  # redirect pra ver_livro = sucesso

    livro_atualizado = Livro.query.get(livro.id)
    assert livro_atualizado.status == StatusLeitura.EM_ANDAMENTO


def test_registrar_leitura_completa_livro(client):
    client.post('/register', data={'username': 'vincenzo', 'senha': '123456'})
    client.post('/login', data={'username': 'vincenzo', 'senha': '123456'})
    client.post('/livros/add', data={
        'titulo': 'O Cortiço',
        'autor': 'Aluísio Azevedo',
        'total_paginas': '200'
    })

    livro = Livro.query.filter_by(titulo='O Cortiço').first()

    # le todas as 200 paginas de uma vez
    client.post(f'/livro/{livro.id}/ler', data={'paginas_lidas': '200'})

    livro_atualizado = Livro.query.get(livro.id)
    assert livro_atualizado.status == StatusLeitura.JA_LIDO


def test_registrar_leitura_paginas_invalidas(client):
    client.post('/register', data={'username': 'vincenzo', 'senha': '123456'})
    client.post('/login', data={'username': 'vincenzo', 'senha': '123456'})
    client.post('/livros/add', data={
        'titulo': 'O Cortiço',
        'autor': 'Aluísio Azevedo',
        'total_paginas': '200'
    })

    livro = Livro.query.filter_by(titulo='O Cortiço').first()

    response = client.post(f'/livro/{livro.id}/ler', data={'paginas_lidas': 'abc'})
    assert response.status_code == 400  # entrada invalida = erro