# IMPORTS
from peewee import Model, PostgresqlDatabase

# SETUP DB
db = PostgresqlDatabase(None)

# CLASS: BASE MODEL
class BaseModel(Model):

    # SUBCLASS: META
    class Meta:
        database = db