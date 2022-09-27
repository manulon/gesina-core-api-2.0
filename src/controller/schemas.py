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


class UserSchema(Schema):
    id = fields.Int()
    first_name = fields.Str()
    last_name = fields.Str()
    email = fields.Str()
    admin_role = fields.Bool()
    active = fields.Bool()


SCHEDULE_TASK_SCHEMA = ScheduleTaskSchema()
USER_SCHEMA = UserSchema()
