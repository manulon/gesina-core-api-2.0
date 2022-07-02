from flask_wtf.form import FlaskForm
from wtforms.validators import DataRequired
from wtforms import (
    IntegerField,
    BooleanField,
    StringField,
    SelectField,
    DateTimeLocalField,
)

from src.view.forms import ErrorMixin
from src.service import geometry_service


class ScheduleConfigForm(FlaskForm, ErrorMixin):
    name = StringField(
        validators=[DataRequired(message="Error: El nombre no puede estar vacío")],
        label="Nombre de la corrida",
    )
    description = StringField(
        validators=[DataRequired(message="Error: La descripción no puede estar vacía")],
        label="Descripción de la corrida",
    )
    start_datetime = DateTimeLocalField(
        validators=[
            DataRequired(message="Error: La fecha de inicio no puede estar vacía")
        ],
        label="Fecha de inicio de la corrida",
        format="%Y-%m-%dT%H:%M",
    )
    geometry_id = SelectField(
        validators=[DataRequired(message="Error: La geometría no puede estar vacía")],
        label="Geometría para usar en la corrida",
        choices=lambda: [
            (geometry.id, geometry.name)
            for geometry in geometry_service.get_geometries()
        ],
    )
    frequency = IntegerField(
        validators=[DataRequired(message="Error: La frecuencia no puede estar vacía")],
        label="Frecuencia de ejecución (en minutos)",
        render_kw={"min": 5},
    )
    enabled = BooleanField(default="disabled", label="Ejecución habilitada")
