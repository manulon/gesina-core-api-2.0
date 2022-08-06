from flask_wtf.form import FlaskForm
from wtforms.validators import DataRequired
from wtforms import (
    IntegerField,
    BooleanField,
    StringField,
    SelectField,
    DateTimeLocalField,
    FileField,
    DecimalField,
    FieldList,
    FormField,
    Form,
)

from src.view.forms import ErrorMixin
from src.service import geometry_service


class InitialFlowForm(Form):
    river = StringField(
        label="River",
        validators=[DataRequired(message="Error: El river no puede estar vacío")],
    )
    reach = StringField(
        label="Reach",
        validators=[DataRequired(message="Error: El reach no puede estar vacío")],
    )
    river_stat = DecimalField(
        label="River stat",
        validators=[DataRequired(message="Error: El river stat no puede estar vacío")],
    )
    flow = DecimalField(
        label="Flow",
        validators=[DataRequired(message="Error: El flow no puede estar vacío")],
    )


class IntervalForm(Form):
    render_kw = {"style": "width: 90px"}

    interval_value = IntegerField(
        label="Valor",
        validators=[DataRequired(message="Error: El intervalo no puede estar vacío")],
        render_kw=render_kw,
    )
    interval_unit = SelectField(
        label="Unidad",
        validators=[DataRequired(message="Error: El intervalo no puede estar vacío")],
        choices=["MINUTE", "HOUR", "DAY", "WEEK"],
    )


class SeriesForm(Form):
    render_kw = {"style": "width: 90px"}
    river = StringField(
        label="River",
        validators=[DataRequired(message="Error: El river no puede estar vacío")],
        render_kw=render_kw,
    )
    reach = StringField(
        label="Reach",
        validators=[DataRequired(message="Error: El reach no puede estar vacío")],
        render_kw=render_kw,
    )
    river_stat = DecimalField(
        label="River stat",
        validators=[DataRequired(message="Error: El river stat no puede estar vacío")],
        render_kw=render_kw,
    )

    border_condition = SelectField(
        label="Condicion de borde",
        validators=[
            DataRequired(message="Error: La condición de borde no puede estar vacía")
        ],
        choices=["Stage Hydrograph", "Flow Hydrograph", "Lateral Inflow Hydrograph"],
    )

    interval = FormField(IntervalForm, label="Intervalo", render_kw=render_kw)

    id_observation = IntegerField(
        label="Id de observación",
        validators=[
            DataRequired(message="Error: El id de observación no puede estar vacío")
        ],
        render_kw=render_kw,
    )

    id_forecast = IntegerField(
        label="Id de pronóstico",
        validators=[
            DataRequired(message="Error: El id de pronóstico no puede estar vacío")
        ],
        render_kw=render_kw,
    )


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

    observation_days = IntegerField(
        validators=[
            DataRequired(message="Error: Los días observados no puede estar vacío")
        ],
        label="Cantidad de dias previos observados",
        render_kw={"min": 0},
    )

    forecast_days = IntegerField(
        validators=[
            DataRequired(message="Error: Los días de pronóstico no pueden estar vacíos")
        ],
        label="Cantidad de días de pronóstico",
        render_kw={"min": 0},
    )

    start_condition_type = SelectField(
        validators=[
            DataRequired(
                message="Error: El tipo de condición inicial no puede estar vacío"
            )
        ],
        label="Tipo de condición inicial",
        choices=["initial_flows", "restart_file"],
    )

    restart_file = FileField(label="Restart file")

    initial_flow_list = FieldList(
        FormField(InitialFlowForm), label="Lista de flujos iniciales", min_entries=0
    )

    series_list = FieldList(
        FormField(SeriesForm), label="Lista de series iniciales", min_entries=0
    )
