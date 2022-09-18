from flask import url_for
from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, ValidationError

from src.view.forms import ErrorMixin


class VerifyPasswords:
    def __init__(self, message):
        self.message = message

    def __call__(self, form, field):
        if form.password.data != field.data:
            raise ValidationError(self.message)


class SingUpForm(FlaskForm, ErrorMixin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "Crear tu cuenta"
        self.endpoint = url_for("public_view_controller.do_sign_up")
        self.show_register_button = False

    email = EmailField(validators=[DataRequired(message="Ingrese un email")])
    first_name = StringField(
        "Nombre", validators=[DataRequired(message="Ingrese un nombre")]
    )
    last_name = StringField(
        "Apellido", validators=[DataRequired(message="Ingrese un apellido")]
    )
    password = PasswordField(
        "Contraseña", validators=[DataRequired(message="Ingrese una contraseña")]
    )
    repeat_password = PasswordField(
        "Confirmación",
        validators=[
            DataRequired(message="Ingrese nuevamente su password"),
            VerifyPasswords(message="Las contraseñas no coinciden"),
        ],
    )
    submit = SubmitField("Registrarse")


class LoginForm(FlaskForm, ErrorMixin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.show_register_button = True
        self.title = "Iniciar sesión"
        self.endpoint = url_for("public_view_controller.do_login")

    email = EmailField(validators=[DataRequired(message="Ingrese un email")])
    password = PasswordField(
        "Contraseña", validators=[DataRequired(message="Ingrese una contraseña")]
    )
    submit = SubmitField("Ingresar")


class EditUserForm(FlaskForm, ErrorMixin):
    def __init__(self, user_id, **kwargs):
        super().__init__(**kwargs)
        self.title = "Edición de Usuario"
        self.endpoint = url_for("user_controller.update_user", user_id=user_id)
        self.show_register_button = False

    email = EmailField(validators=[DataRequired(message="Ingrese un email")])
    first_name = StringField(
        "Nombre", validators=[DataRequired(message="Ingrese un nombre")]
    )
    last_name = StringField(
        "Apellido", validators=[DataRequired(message="Ingrese un apellido")]
    )
    admin_role = BooleanField(
        "Administrador", validators=[]
    )
    password = PasswordField(
        "Contraseña", validators=[]
    )
    repeat_password = PasswordField(
        "Confirmación",
        validators=[
            VerifyPasswords(message="Las contraseñas no coinciden"),
        ],
    )
    submit = SubmitField("Guardar")
