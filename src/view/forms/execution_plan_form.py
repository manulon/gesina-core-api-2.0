from flask_wtf.form import FlaskForm
from wtforms.validators import DataRequired
from wtforms import StringField, IntegerField, Form, HiddenField, FieldList, FormField
from flask_wtf.file import FileField, FileRequired

from src.view.forms import ErrorMixin


class ExecutionPlanOutputForm(Form):
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


class ExecutionPlanForm(FlaskForm, ErrorMixin):
    plan_name = StringField(
        validators=[DataRequired(message="Error: Ingrese un nombre de plan")]
    )
    geometry_option = IntegerField(
        validators=[DataRequired(message="Error: Seleccione una geometría")]
    )
    project_file = FileField(
        validators=[FileRequired(message="Error: Seleccione un archivo")]
    )
    plan_file = FileField(
        validators=[FileRequired(message="Error: Seleccione un archivo")]
    )
    flow_file = FileField(
        validators=[FileRequired(message="Error: Seleccione un archivo")]
    )
    restart_file = FileField()
    execution_plan_output_list = FieldList(
        FormField(ExecutionPlanOutputForm),
        label="Lista de resultados a exportar a CSV",
        min_entries=0,
    )
