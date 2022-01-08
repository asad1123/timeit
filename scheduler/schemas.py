from marshmallow import Schema, fields

# ----------------------------------------------------------------------------

class Timer(Schema):
    id = fields.UUID(load_only=True)
    expiry_time = fields.Int()
    url = fields.URL()