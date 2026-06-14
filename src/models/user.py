# IMPORTS
from datetime import datetime
from peewee import CharField, DateTimeField
from .base import BaseModel

# CLASS: USER
class User(BaseModel):
    username = CharField(unique=True)
    email = CharField(unique=True)
    password_hash = CharField()
    two_factor_code_hash = CharField(null=True)
    two_factor_code_expires_at = DateTimeField(null=True)
    created_at = DateTimeField(default=datetime.utcnow)

    # SUBCLASS: META
    class Meta:
        table_name = "users"
