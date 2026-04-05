from peewee import (CharField, TextField, IntegerField, ForeignKeyField, DateTimeField)
from datetime import datetime
from .base import BaseModel
from .board import Board
from .lane import Lane

# CLASS: TASK
class Task(BaseModel):
    board = ForeignKeyField(Board, backref="tasks", on_delete="CASCADE")
    lane = ForeignKeyField(Lane, backref="tasks", on_delete="RESTRICT")
    title = CharField()
    description = TextField(null=True)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    # SUBCLASS: META
    class Meta:
        table_name = "tasks"
        indexes = ()