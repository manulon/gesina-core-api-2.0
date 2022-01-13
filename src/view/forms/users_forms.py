from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, PasswordField
from wtforms.validators import DataRequired


class SingUpForm(FlaskForm):
    email = EmailField(validators=[DataRequired(message="Ingrese un email")])

    first_name = StringField(validators=[DataRequired(message="Ingrese un nombre")])

    last_name = StringField(validators=[DataRequired(message="Ingrese un apellido")])

    password = PasswordField(validators=[DataRequired(message="Ingrese un password")])
