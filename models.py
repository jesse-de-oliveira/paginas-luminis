from flask_sqlalchemy import SQLAlchemy
from enum import Enum
from datetime import datetime, timezone

db = SQLAlchemy()

class StatusLeitura(Enum):
    QUERO_LER = "Quero Ler"
    EM_ANDAMENTO = "Em Andamento"
    JA_LIDO = "Já Lido"

class TipoDiario(Enum):
    RESUMO = "resumo"
    REFLEXAO = "reflexao"
    COMENTARIO = "comentario"

class TipoDesafio(Enum):
    DIARIO = "diario"
    SEMANAL = "semanal"

class Usuario(db.Model):                                                
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    senha = db.Column(db.String(200), nullable=False)
    nome = db.Column(db.String(120), nullable=True)

    livros = db.relationship('Livro', backref='usuario', cascade="all, delete-orphan")
    leituras = db.relationship('Leitura', backref='usuario', cascade="all, delete-orphan")
    diarios = db.relationship('Diario', backref='usuario', cascade="all, delete-orphan")
    frases = db.relationship('FraseFavorita', backref='usuario', cascade="all, delete-orphan")
    desafios = db.relationship('UsuarioDesafio', backref='usuario', cascade="all, delete-orphan")
    conquistas = db.relationship('UsuarioConquista', backref='usuario', cascade="all, delete-orphan")

class Livro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    autor = db.Column(db.String(200), nullable=False)
    total_paginas = db.Column(db.Integer, nullable=True)
    status = db.Column(db.Enum(StatusLeitura), nullable=False, default=StatusLeitura.QUERO_LER)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    leituras = db.relationship('Leitura', backref='livro', cascade="all, delete-orphan")
    frases = db.relationship('FraseFavorita', backref='livro', cascade="all, delete-orphan")

class Leitura(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    paginas_lidas = db.Column(db.Integer)
    tempo_lido_min = db.Column(db.Integer)
    livro_id = db.Column(db.Integer, db.ForeignKey('livro.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)

class Diario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    data = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    tipo = db.Column(db.Enum(TipoDiario), nullable=False)
    conteudo = db.Column(db.Text, nullable=False)
    livro_id = db.Column(db.Integer, db.ForeignKey('livro.id'), nullable=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)

class FraseFavorita(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    texto = db.Column(db.Text, nullable=False)
    pagina = db.Column(db.Integer, nullable=True)
    nome_autor = db.Column(db.String(200), nullable=True)
    livro_id = db.Column(db.Integer, db.ForeignKey('livro.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)

class Desafio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(200), nullable=False)
    tipo = db.Column(db.Enum(TipoDesafio), nullable=False)

class UsuarioDesafio(db.Model):
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), primary_key=True)
    desafio_id = db.Column(db.Integer, db.ForeignKey('desafio.id'), primary_key=True)
    concluido = db.Column(db.Boolean, default=False)
    data_conclusao = db.Column(db.DateTime, nullable=True)

class Conquista(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200), nullable=False)
    descricao = db.Column(db.Text, nullable=True)

class UsuarioConquista(db.Model):
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), primary_key=True)
    conquista_id = db.Column(db.Integer, db.ForeignKey('conquista.id'), primary_key=True)
    data_conquista = db.Column(db.DateTime, nullable=False, default=datetime.now(timezone.utc))
    conquista = db.relationship('Conquista', backref='usuarios')

   