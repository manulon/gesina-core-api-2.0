from marshmallow import Schema, fields, post_load


class ActivityParams(Schema):
    refresh_rate = fields.Integer(missing=-1)
    date_from = fields.String()
    date_to = fields.String()


class BorderConditionSchema(Schema):
    id = fields.Int()
    scheduled_task_id = fields.Int()
    river = fields.Str()
    reach = fields.Str()
    river_stat = fields.Str()
    interval = fields.Str()
    type = fields.Str()  # Assuming type is a string representation of the Enum
    series_id = fields.Int()


class PlanSeriesSchema(Schema):
    id = fields.Int()
    river = fields.Str()
    reach = fields.Str()
    river_stat = fields.Str()
    stage_series_id = fields.Int()
    flow_series_id = fields.Int()
    scheduled_task_id = fields.Int()


class InitialFlowSchema(Schema):
    id = fields.Int()
    scheduled_task_id = fields.Int()
    river = fields.Str()
    reach = fields.Str()
    river_stat = fields.Str()
    flow = fields.Str()


class ScheduleTaskSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    description = fields.Str()
    frequency = fields.Int()
    created_at = fields.DateTime("%Y-%m-%dT%H:%M:%S")
    start_datetime = fields.DateTime()
    enabled = fields.Bool()
    geometry = fields.Str()  # Ensure this correctly serializes the Geometry relationship
    user = fields.Str()  # Ensure this correctly serializes the User relationship
    initial_flows = fields.List(fields.Nested(InitialFlowSchema))
    border_conditions = fields.List(fields.Nested(BorderConditionSchema))
    plan_series_list = fields.List(fields.Nested(PlanSeriesSchema))
    start_condition_type = fields.Str()


class UserSchema(Schema):
    id = fields.Int()
    first_name = fields.Str()
    last_name = fields.Str()
    email = fields.Str()
    admin_role = fields.Bool()
    active = fields.Bool()


SCHEDULE_TASK_SCHEMA = ScheduleTaskSchema()
USER_SCHEMA = UserSchema()
