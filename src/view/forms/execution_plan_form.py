from flask_wtf.form import FlaskForm
from wtforms.validators import DataRequired
from wtforms import StringField, IntegerField
from flask_wtf.file import FileField, FileRequired

from src.view.forms import ErrorMixin


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
