# IMPORTS
from peewee import CharField, TextField, ForeignKeyField, DateTimeField
from datetime import datetime
from .base import BaseModel
from .lane import Lane

# CLASS: TASK
class Task(BaseModel):
    lane = ForeignKeyField(Lane, backref="tasks", on_delete="RESTRICT")
    title = CharField()
    description = TextField(null=True)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    # SUBCLASS: META
    class Meta:
        table_name = "tasks"