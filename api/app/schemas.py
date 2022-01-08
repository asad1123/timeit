from marshmallow import Schema, fields

# ----------------------------------------------------------------------------


class TimerSchema(Schema):
    id = fields.UUID(dump_only=True)

    hours = fields.Int(load_only=True, required=True)
    minutes = fields.Int(load_only=True, required=True)
    seconds = fields.Int(load_only=True, required=True)
    url = fields.URL(relative=False, load_only=True, required=True)

    time_left = fields.Int(dump_only=True)
