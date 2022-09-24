from marshmallow import Schema, fields


class ActivityParams(Schema):
    refresh_rate = fields.Integer(missing=-1)
    date_from = fields.String()
    date_to = fields.String()


class ScheduleTaskSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    description = fields.Str()
    frequency = fields.Int()
    created_at = fields.DateTime("%Y-%m-%dT%H:%M:%S")
    start_datetime = fields.DateTime()
    enabled = fields.Bool()
    geometry = fields.Str()
    user = fields.Str()


SCHEDULE_TASK_SCHEMA = ScheduleTaskSchema()
