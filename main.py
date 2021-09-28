from datetime import datetime
from flask import Flask, jsonify, redirect, render_template, request, url_for, flash
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

import data
import forms
import json
import os
import random

app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY") or "this-is-the-secret-key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///nutrixion.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message = u"Inicia sesión para acceder a esta página."


@login_manager.user_loader
def load_user(user_id):
    return data.Usuario.query.get(int(user_id))


@app.route("/")
@login_required
def inicio():
    desayuno = random.choice(data.Comida.query.filter_by(tipo="Desayuno").all())
    comida = random.choice(data.Comida.query.filter_by(tipo="Comida").all())
    cena = random.choice(data.Comida.query.filter_by(tipo="Cena").all())
    colacion = random.choice(data.Comida.query.filter_by(tipo="Colación").all())

    clientes = [cliente for cliente in data.get_clients() if cliente.activo == 1]

    return render_template("index.html", comidas=[desayuno, comida, cena, colacion], clientes=clientes)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = data.Usuario.query.filter_by(usuario=request.form["correo"]).first()
        contrasena = request.form["contrasena"]

        if not usuario:
            flash("El usuario no existe.")
            return redirect(url_for("login"))

        if not check_password_hash(usuario.contrasena, contrasena):
            flash("La contraseña es incorrecta.")
            return redirect(url_for("login"))

        login_user(usuario)
        return redirect(url_for("inicio"))

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        contrasena = request.form["contrasena"]
        confirmar_contrasena = request.form["confirmarContrasena"]

        if contrasena != confirmar_contrasena:
            flash("Las contraseñas no coinciden.")
            return redirect(url_for("registro"))

        nuevo_hash = generate_password_hash(contrasena, method='pbkdf2:sha256', salt_length=8)

        usuario = data.Usuario(
            tipo=1,
            nombre=request.form["nombre"],
            usuario=request.form["correo"],
            contrasena=nuevo_hash,
            activo=1
        )
        db.session.add(usuario)
        db.session.commit()

        return redirect(url_for("inicio"))

    return render_template("register.html")


@app.route("/clientes")
@login_required
def clientes():
    clientes = [cliente for cliente in data.get_clients() if cliente.activo == 1]
    form = forms.AgregarClienteForm()
    return render_template("clientes.html", clientes=clientes, form=form)


@app.route("/clientes/<id_cliente>")
@login_required
def ver_cliente(id_cliente):
    cliente = data.get_client(id_cliente)
    dietas = [dieta for dieta in data.get_diets(id_cliente) if dieta.activo == 1]
    form = forms.AgregarDietaForm()
    return render_template("ver-cliente.html", cliente=cliente, dietas=dietas, form=form)


@app.route("/clientes/add", methods=["GET", "POST"])
@login_required
def agregar_cliente():
    if request.method == "POST":
        fecha_inicio = datetime.strptime(request.form["fecha_inicio"], "%Y-%m-%d").strftime("%d/%m/%Y")

        cliente = data.Cliente(
            nombre=request.form["nombre"],
            edad=request.form["edad"],
            peso=request.form["peso"],
            fecha_inicio=fecha_inicio,
            usuario=current_user.id,
            activo=1
        )

        db.session.add(cliente)
        db.session.commit()

        return redirect(url_for("clientes"))

    form = forms.AgregarClienteForm()
    return render_template("agregar-cliente.html", form=form)


@app.route("/clientes/<id_cliente>/edit", methods=["POST"])
@login_required
def editar_cliente(id_cliente):
    fecha_inicio = datetime.strptime(request.form["fecha_inicio"], "%Y-%m-%d").strftime("%d/%m/%Y")

    cliente = data.Cliente(
        nombre=request.form["nombre"],
        edad=request.form["edad"],
        peso=request.form["peso"],
        fecha_inicio=fecha_inicio,
        usuario=current_user.id,
        activo=1
    )
    data.update_client(id_cliente, cliente)
    return redirect(url_for("clientes"))


@app.route("/clientes/<id_cliente>/delete")
@login_required
def eliminar_cliente(id_cliente):
    data.delete_client(id_cliente)
    return redirect(url_for("clientes"))


@app.route("/comidas")
@login_required
def comidas():
    comidas = [comida for comida in data.get_meals() if comida.activo == 1]
    form = forms.AgregarComidaForm()
    return render_template("comidas.html", comidas=comidas, form=form)


@app.route("/api/comidas")
def api_comidas():
    comidas = data.get_meals(request.args)
    return jsonify(comidas=[comida.to_dict() for comida in comidas])


@app.route("/api/comidas/<id_comida>")
def api_comida(id_comida):
    comida = data.get_meal(id_comida)
    return jsonify(comida=comida.to_dict())


@app.route("/comidas/add", methods=["GET", "POST"])
@login_required
def agregar_comida():
    if request.method == "POST":
        comida = data.Comida(
            tipo=request.form["tipo"],
            nombre=request.form["nombre"],
            descripcion=request.form["descripcion"],
            calorias=request.form["calorias"],
            activo=1
        )
        db.session.add(comida)
        db.session.commit()

        return redirect(url_for("comidas"))

    form = forms.AgregarComidaForm()
    return render_template("agregar-comida.html", form=form)


@app.route("/comidas/<id_comida>/edit", methods=["POST"])
@login_required
def editar_comida(id_comida):
    comida = data.Comida(
        tipo=request.form["tipo"],
        nombre=request.form["nombre"],
        descripcion=request.form["descripcion"],
        calorias=request.form["calorias"]
    )
    data.update_meal(id_comida, comida)
    return redirect(url_for("comidas"))


@app.route("/comidas/<id_comida>/delete")
@login_required
def eliminar_comida(id_comida):
    data.delete_meal(id_comida)
    return redirect(url_for("comidas"))


@app.route("/clientes/<id_cliente>/dietas/add", methods=["GET", "POST"])
@login_required
def agregar_dieta(id_cliente):
    if request.method == "POST":
        fecha = datetime.strptime(request.form["fecha"], "%Y-%m-%d").strftime("%d/%m/%Y")
        duracion = int(request.form["duracion"])
        menu = json.dumps(
            {"dieta": [{"dia": n + 1, "desayuno": "", "comida": "", "cena": ""} for n in range(duracion)]})
        print(menu)

        dieta = data.Dieta(
            id_cliente=id_cliente,
            fecha=fecha,
            calorias=request.form["calorias"],
            duracion=duracion,
            menu=menu,
            notas=request.form["notas"],
            activo=1
        )
        db.session.add(dieta)
        db.session.commit()

        return redirect(url_for("ver_cliente", id_cliente=id_cliente))

    form = forms.AgregarDietaForm()
    return render_template("agregar-dieta.html", form=form, id_cliente=id_cliente)


@app.route("/dietas/<id_dieta>")
@login_required
def ver_dieta(id_dieta):
    dieta = data.get_diet(id_dieta)
    menu = json.loads(dieta.menu)["dieta"]
    print(menu[0])

    meals = data.get_meals()
    form = forms.AgregarMenuForm()
    form.desayuno.choices = [(meal.id, f"{meal.nombre} ({meal.calorias} calorías)") for meal in meals if
                             meal.tipo == "Desayuno"]
    form.comida.choices = [(meal.id, f"{meal.nombre} ({meal.calorias} calorías)") for meal in meals if
                           meal.tipo == "Comida"]
    form.cena.choices = [(meal.id, f"{meal.nombre} ({meal.calorias} calorías)") for meal in meals if
                         meal.tipo == "Cena"]

    return render_template("ver-dieta.html", dieta=dieta, menu=data.expand_menu(menu), form=form)


@app.route("/dietas/<id_dieta>/edit")
@login_required
def editar_dieta(id_dieta):
    return redirect(url_for("clientes"))


@app.route("/dietas/<id_dieta>/delete")
@login_required
def eliminar_dieta(id_dieta):
    dieta = data.get_diet(id_dieta)
    data.delete_diet(id_dieta)
    return redirect(url_for("ver_cliente", id_cliente=dieta.id_cliente))


@app.route("/clientes/<id_cliente>/dietas/<id_dieta>/menu/add", methods=["GET", "POST"])
@login_required
def agregar_menu(id_cliente, id_dieta):
    dieta = data.get_diet(id_dieta)
    menu = data.get_menu(dieta)

    if request.method == "POST":
        nuevo_dia = {
            "dia": len(menu) + 1,
            "desayuno": request.form["desayuno"],
            "comida": request.form["comida"],
            "cena": request.form["cena"]
        }
        nuevo_menu = data.update_menu(dieta.menu, nuevo_dia)
        data.update_diet(dieta=dieta, menu=nuevo_menu)

        return redirect(url_for("ver_dieta", id_dieta=id_dieta))

    meals = data.get_meals()

    form = forms.AgregarMenuForm()
    form.desayuno.choices = [(meal.id, f"{meal.nombre} ({meal.calorias} calorías)") for meal in meals if
                             meal.tipo == "Desayuno"]
    form.comida.choices = [(meal.id, f"{meal.nombre} ({meal.calorias} calorías)") for meal in meals if
                           meal.tipo == "Comida"]
    form.cena.choices = [(meal.id, f"{meal.nombre} ({meal.calorias} calorías)") for meal in meals if
                         meal.tipo == "Cena"]
    return render_template("agregar-menu.html", form=form, dieta=dieta, menu=menu)


@app.route("/menu/<id_dieta>/<dia>/edit", methods=["POST"])
@login_required
def editar_menu(id_dieta, dia):
    dia = int(dia)
    dieta = data.get_diet(id_dieta)
    menu = json.loads(dieta.menu)["dieta"]

    menu[dia - 1]["desayuno"] = request.form["desayuno"]
    menu[dia - 1]["comida"] = request.form["comida"]
    menu[dia - 1]["cena"] = request.form["cena"]
    new_menu = json.dumps({"dieta": menu})

    data.update_menu(id_dieta, new_menu)

    return redirect(url_for("ver_dieta", id_dieta=id_dieta))


if __name__ == "__main__":
    app.run(debug=True)
