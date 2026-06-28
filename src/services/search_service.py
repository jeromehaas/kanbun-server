# IMPORTS
from peewee import fn
from src.models import Board, Lane, Task, db

# FUNCTION: SERIALIZE SEARCH RESULT
def _serialize_search_result(task):

    # RETURN
    return {
        "task_id": task.id,
        "title": task.title,
        "description": task.description or "",
        "board_id": task.lane.board.id,
        "board_name": task.lane.board.name,
        "lane_id": task.lane.id,
        "lane_name": task.lane.name,
    }


# FUNCTION: SEARCH TASK DOCUMENTS
def search_task_documents(query, limit=20):

    # NORMALIZE QUERY
    normalized_query = query.strip()

    # RETURN EMPTY RESULTS FOR EMPTY QUERIES
    if not normalized_query:
        return []

    # BUILD SEARCH PATTERN
    search_pattern = f"%{ normalized_query }%"

    # QUERY TASKS ACROSS TITLES, DESCRIPTIONS, LANES, AND BOARDS
    with db.connection_context():
        tasks = list(
            Task.select(Task, Lane, Board)
            .join(Lane)
            .join(Board)
            .where(
                (Task.title ** search_pattern) |
                (fn.COALESCE(Task.description, "") ** search_pattern) |
                (Lane.name ** search_pattern) |
                (Board.name ** search_pattern)
            )
            .order_by(Board.name, Lane.position, Task.position, Task.id)
            .limit(limit)
        )

    # RETURN SERIALIZED RESULTS
    return [_serialize_search_result(task) for task in tasks]
