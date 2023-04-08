from flask_wtf.form import FlaskForm
from wtforms.validators import DataRequired
from wtforms import (
    IntegerField,
    BooleanField,
    StringField,
    SelectField,
    DateTimeLocalField,
    FileField,
    FieldList,
    FormField,
    Form,
    HiddenField,
)

from src.persistance.scheduled_task import BorderConditionType
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
    river_stat = StringField(
        label="River stat",
        validators=[DataRequired(message="Error: El river stat no puede estar vacío")],
    )
    flow = StringField(
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
    render_kw = {"style": "width: 80px"}
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
    river_stat = StringField(
        label="River stat",
        validators=[DataRequired(message="Error: El river stat no puede estar vacío")],
        render_kw=render_kw,
    )

    border_condition = SelectField(
        label="Condicion de borde",
        validators=[
            DataRequired(message="Error: La condición de borde no puede estar vacía")
        ],
        choices=BorderConditionType.choices(),
    )

    interval = FormField(IntervalForm, label="Intervalo", render_kw=render_kw)

    series_id = IntegerField(
        label="Id de serie",
        validators=[
            DataRequired(message="Error: El id de series no puede estar vacío")
        ],
        render_kw=render_kw,
    )


class PlanSeriesForm(Form):
    render_kw = {"style": "width: 120px"}
    idx = HiddenField(default=None)
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
    river_stat = StringField(
        label="River stat",
        validators=[DataRequired(message="Error: El river stat no puede estar vacío")],
        render_kw=render_kw,
    )

    stage_series_id = IntegerField(
        label="Id de serie de altura",
        validators=[DataRequired(message="Error: El id no puede estar vacío")],
        render_kw=render_kw,
    )

    flow_series_id = IntegerField(
        label="Id de serie de flujo",
        validators=[DataRequired(message="Error: El id no puede estar vacío")],
        render_kw=render_kw,
    )


class ScheduleConfigForm(FlaskForm, ErrorMixin):
    idx = HiddenField(default=None)
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
    calibration_id = IntegerField(
        validators=[
            DataRequired(message="Error: El ID de calibrados no puede estar vacío")
        ],
        label="ID de calibrados",
    )
    enabled = BooleanField(label="Ejecución habilitada")

    project_file = FileField(label="Archivo de proyecto (.prj)")
    project_file_present = HiddenField(default=False)

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
    restart_file_present = HiddenField(default=False)
    initial_flow_file = FileField(label="Importar series iniciales desde .CSV")

    initial_flow_list = FieldList(
        FormField(InitialFlowForm), label="Lista de flujos iniciales", min_entries=0
    )

    series_list_file = FileField(label="Importar series de borde desde .CSV")
    series_list = FieldList(
        FormField(SeriesForm), label="Lista de series iniciales", min_entries=0
    )

    plan_file = FileField(label="Archivo de Plan (.p)")
    plan_file_present = HiddenField(default=False)
    plan_series_file = FileField(label="Importar series de salida desde .CSV")
    plan_series_list = FieldList(
        FormField(PlanSeriesForm), label="Lista de series del plan", min_entries=0
    )

    calibration_id_for_simulations = IntegerField(
        validators=[
            DataRequired(
                message="Error: El ID de calibrados para las simulaciones no puede estar vacío"
            )
        ],
        label="ID de calibrados para las simulaciones",
    )
