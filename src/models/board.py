# IMPORTS
from peewee import CharField, DateTimeField
from datetime import datetime
from .base import BaseModel

# CLASS: BOARD
class Board(BaseModel):
    name = CharField(unique=True)
    created_at = DateTimeField(default=datetime.utcnow)

    # SUBCLASS: META
    class Meta:
        table_name = "boards"