from wtforms import Form, DateField, DecimalField, IntegerField, SelectField, StringField, SubmitField, validators


class AgregarClienteForm(Form):
    nombre = StringField('Nombre', [validators.DataRequired()])
    edad = StringField('Edad', [validators.DataRequired(), validators.NumberRange(min=5, max=120)])
    peso = DecimalField('Peso', [validators.DataRequired(), validators.NumberRange(min=10, max=500)])
    fecha_inicio = DateField('Fecha de Inicio', [validators.DataRequired()])
    enviar = SubmitField('Enviar')


class AgregarComidaForm(Form):
    tipo = SelectField('Tipo', [validators.DataRequired()], choices=["Desayuno", "Comida", "Cena", "Colación"])
    nombre = StringField('Nombre', [validators.DataRequired()])
    descripcion = StringField('Descripción', [validators.DataRequired()])
    calorias = IntegerField('Calorías', [validators.DataRequired(), validators.NumberRange(min=0, max=5000)])
    dieta = SelectField('Dieta', choices=["", "Vegana", "Keto"])
    enviar = SubmitField('Enviar')


class AgregarDietaForm(Form):
    fecha = DateField('Fecha', [validators.DataRequired()])
    calorias = IntegerField('Calorías', [validators.DataRequired(), validators.NumberRange(min=500, max=3000)])
    duracion = IntegerField('Duración', [validators.DataRequired(), validators.NumberRange(min=1, max=30)])
    notas = StringField('Notas')
    enviar = SubmitField('Enviar')


class AgregarMenuForm(Form):
    desayuno = SelectField('Desayuno', [validators.DataRequired()])
    comida = SelectField('Comida', [validators.DataRequired()])
    cena = SelectField('Cena', [validators.DataRequired()])
    enviar = SubmitField('Enviar')
