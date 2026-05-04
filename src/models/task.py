# IMPORTS
from peewee import CharField, TextField, ForeignKeyField, DateTimeField
from datetime import datetime
from .base import BaseModel
from .lane import Lane

# CLASS: TASK
class Task(BaseModel):
    # TODO: on_delete="RESTRICT" conflicts with lane.delete_instance(recursive=True) in the delete controller.
    # Consider changing to on_delete="CASCADE" so lane deletion cleanly removes tasks at the DB level.
    lane = ForeignKeyField(Lane, backref="tasks", on_delete="RESTRICT")
    title = CharField()
    description = TextField(null=True)
    created_at = DateTimeField(default=datetime.utcnow)
    # TODO: updated_at is never refreshed on save — override save() to update this field automatically
    updated_at = DateTimeField(default=datetime.utcnow)

    # SUBCLASS: META
    class Meta:
        table_name = "tasks"