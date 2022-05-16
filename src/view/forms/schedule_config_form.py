from flask_wtf.form import FlaskForm
from wtforms.validators import DataRequired
from wtforms import IntegerField, BooleanField

from src.view.forms import ErrorMixin


class ScheduleConfigForm(FlaskForm, ErrorMixin):
    frequency = IntegerField(
        validators=[DataRequired(message="Error: La frecuencia no puede estar vacía")]
    )
    schedule_config_enabled = BooleanField(default="disabled")
