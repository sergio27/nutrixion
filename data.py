import json
from datetime import datetime
from flask_login import UserMixin, current_user
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Comida(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(80), nullable=False)
    nombre = db.Column(db.String(120), nullable=False)
    descripcion = db.Column(db.String(120), nullable=False)
    calorias = db.Column(db.Integer, nullable=False)
    liga = db.Column(db.String(120))
    activo = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return '<Comida %r>' % self.nombre

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), nullable=False)
    edad = db.Column(db.Integer, nullable=False)
    peso = db.Column(db.Numeric, nullable=False)
    fecha_inicio = db.Column(db.String(10), nullable=False)
    usuario = db.Column(db.Integer, nullable=False)
    activo = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return "<Cliente %r>" % self.nombre

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


class Dieta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_cliente = db.Column(db.Integer, nullable=False)
    fecha = db.Column(db.String(10), nullable=False)
    calorias = db.Column(db.Integer, nullable=False)
    duracion = db.Column(db.Integer, nullable=False)
    menu = db.Column(db.String(), nullable=False)
    notas = db.Column(db.String(250), nullable=False)
    activo = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return "<Dieta %r>" % self.fecha

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.Integer, nullable=False)
    nombre = db.Column(db.String(), nullable=False)
    usuario = db.Column(db.String(), nullable=False)
    contrasena = db.Column(db.String(), nullable=False)
    activo = db.Column(db.Integer, nullable=False)


def get_meal(id_comida):
    comida = Comida.query.filter_by(id=id_comida).first()
    return comida


def get_meals(args=[]):
    comidas = db.session.query(Comida).all()

    if "tipo" in args:
        comidas = [comida for comida in comidas if comida.tipo == args.get("tipo")]
    if "calorias" in args:
        comidas = [comida for comida in comidas if comida.calorias <= int(args.get("calorias"))]
    if "dieta" in args:
        comidas = [comida for comida in comidas if comida.dieta <= int(args.get("dieta"))]

    return comidas


def update_meal(id_comida, comida_update):
    comida = Comida.query.get(id_comida)
    comida.tipo = comida_update.tipo
    comida.nombre = comida_update.nombre
    comida.descripcion = comida_update.descripcion
    comida.calorias = comida_update.calorias

    db.session.commit()


def delete_meal(id_comida):
    comida = Comida.query.get(id_comida)
    comida.activo = 0
    db.session.commit()


def get_clients():
    clientes = Cliente.query.filter_by(usuario=current_user.id)
    return clientes


def get_client(id_cliente):
    cliente = Cliente.query.filter_by(id=id_cliente).first()
    return cliente


def update_client(id_cliente, cliente_update):
    cliente = Cliente.query.get(id_cliente)
    cliente.nomnre = cliente_update.nombre
    cliente.edad = cliente_update.edad
    cliente.peso = cliente_update.peso
    cliente.fecha_inicio = cliente_update.fecha_inicio

    db.session.commit()


def delete_client(id_cliente):
    cliente = Cliente.query.get(id_cliente)
    cliente.activo = 0
    db.session.commit()


def get_diets(id_cliente):
    dietas = Dieta.query.filter_by(id_cliente=id_cliente)
    return dietas


def get_diet(id_dieta):
    dieta = Dieta.query.filter_by(id=id_dieta).first()
    return dieta


def delete_diet(id_dieta):
    dieta = Dieta.query.get(id_dieta)
    dieta.activo = 0
    db.session.commit()


def expand_menu(menu):
    expanded_menu = menu.copy()

    for dia in expanded_menu:
        dia["desayuno"] = get_meal(dia["desayuno"]).to_dict() if dia["desayuno"] != "" else ""
        dia["comida"] = get_meal(dia["comida"]).to_dict() if dia["comida"] != "" else ""
        dia["cena"] = get_meal(dia["cena"]).to_dict() if dia["cena"] != "" else ""

    return expanded_menu


def update_menu(id_dieta, menu):
    dieta = Dieta.query.filter_by(id=id_dieta).first()
    dieta.menu = menu

    db.session.commit()


def update_diet(dieta, menu):
    dieta_original = Dieta.query.filter_by(id=dieta.id).first()
    dieta_original.menu = json.dumps(menu)

    db.session.commit()
