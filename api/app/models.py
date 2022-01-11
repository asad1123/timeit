from pymodm import fields, MongoModel

# ----------------------------------------------------------------------------


class Timer(MongoModel):
    id = fields.UUIDField(primary_key=True)
    expiry_time = fields.IntegerField()
    url = fields.URLField()
