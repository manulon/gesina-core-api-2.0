from flask_wtf.form import FlaskForm
from wtforms import StringField, validators
from flask_wtf.file import FileField, FileRequired

from src.view.forms import ErrorMixin


class GeometryForm(FlaskForm, ErrorMixin):
    description = StringField(
        [
            validators.Length(max=256),
            validators.DataRequired(message="Error: Ingrese una descripción"),
        ]
    )
    file = FileField(validators=[FileRequired(message="Error: Seleccione un archivo")])
