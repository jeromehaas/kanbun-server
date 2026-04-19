# IMPORTS
from datetime import datetime
from peewee import CharField, IntegerField, ForeignKeyField, DateTimeField
from .base import BaseModel
from .board import Board

# CLASS: LANE
class Lane(BaseModel):
    board = ForeignKeyField(Board, backref="lanes", on_delete="CASCADE")
    name = CharField()
    position = IntegerField()
    created_at = DateTimeField(default=datetime.utcnow)

    # SUBCLASS: META
    class Meta:
        table_name = "lanes"
        indexes = (
            (("board", "name"), True),
        )