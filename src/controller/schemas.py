from marshmallow import Schema, fields


class ActivityParams(Schema):
    refresh_rate = fields.Integer(missing=-1)
    date_from = fields.String()
    date_to = fields.String()
