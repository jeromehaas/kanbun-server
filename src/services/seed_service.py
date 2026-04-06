# IMPORTS
from peewee import prefetch
from src.models import db, Board, Lane, Task
from src.data.seed_data.boards import BOARDS
from src.data.seed_data.lanes import LANES
from src.data.seed_data.tasks import TASKS

# FUNCTION: RESET DATABASE
def reset_database():
    Task.delete().execute()
    Lane.delete().execute()
    Board.delete().execute()

# FUNCTION: SEED BOARDS
def seed_boards():

    # DEFINE BOARDS LISET
    created_boards = {}

    # ADD BOARDS TO BOARD LIST
    for board_data in BOARDS:

        # CREATE BOARD
        board = Board.create(
            name=board_data["name"],
        )

        # ADD KEY TO BOARD
        created_boards[board_data["key"]] = board

    # RETURN
    return created_boards

# FUNCTION: SEED LANES
def seed_lanes(created_boards):

    # DEFINE LANES LIST
    created_lanes = {}

    # LOOP OVER LANES
    for lane_data in LANES:

        # GET BOARD
        board = created_boards.get(lane_data["board_key"])

        # CHECK FOR BOARD
        if board is None:
            raise ValueError(
                "UNKNOWN BOARD KEY"
            )

        # CREATE LANE
        lane = Lane.create(
            board=board,
            name=lane_data["name"],
            position=lane_data["position"],
        )

        # GET LANE KEY
        created_lanes[(lane_data["board_key"], lane_data["key"])] = lane

    # RETURN
    return created_lanes

# FUNCTION: SEED TASKS
def seed_tasks(created_boards, created_lanes):

    # DEFINE TASKS
    created_tasks = []

    # LOOP OVER TASKS
    for task_data in TASKS:

        # GET BOARD
        board = created_boards.get(task_data["board_key"])

        # CHECK FOR BOARD
        if board is None:
            raise ValueError(
                "UNKNOWN BOARD KEY IN TASKS"
            )

        # CREATE LANE
        lane = created_lanes.get((task_data["board_key"], task_data["lane_key"]))

        # CHECK FOR LANE
        if lane is None:
            raise ValueError(
                f'UNKNOWN lane_key "{task_data["lane_key"]}" '
                f'FOR board_key "{task_data["board_key"]}" IN TASKS'
            )

        # CREATE TAKS
        task = Task.create(
            board=board,
            lane=lane,
            title=task_data["title"],
            description=task_data.get("description"),
        )

        # ADD TASK TO TASK LIST
        created_tasks.append(task)

    # RETURN
    return created_tasks

# FUNCTION: SERIALIZED SEEDED DATA
def serialize_seeded_data():

    # PREFETCH BOARDS
    boards = prefetch(
        Board.select().order_by(Board.id),
        Lane.select().order_by(Lane.position),
        Task.select().order_by(Task.id),
    )

    # DEFINE BOARD LIST
    board_list = []

    # LOOP OVER BOARDS
    for board in boards:

        # DEFINE LANE LIST
        lane_list = []

        # LOOP OVER LANES
        for lane in board.lanes:

            # DEFINE TASKS LIST
            task_list = []

            # ADD TAKS TO TAKS LIST
            for task in lane.tasks:
                task_list.append({
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                })

            # ADD  LANES TO LANE LIST
            lane_list.append({
                "id": lane.id,
                "name": lane.name,
                "position": lane.position,
                "tasks": task_list,
            })

        # ADD BOARD TO BOARD LIST
        board_list.append({
            "id": board.id,
            "name": board.name,
            "lanes": lane_list,
        })

    # RETURN
    return board_list

# FUNCTION: RUN SEED
def run_seed():

    # RUN STEPS
    with db.atomic():

        # RESET ALL ENTRIES
        reset_database()

        # CREATE BOARDS, LANES AND TAKS
        created_boards = seed_boards()
        created_lanes = seed_lanes(created_boards)
        created_tasks = seed_tasks(created_boards, created_lanes)

        # RETURN
        return {
            "boards_count": len(created_boards),
            "lanes_count": len(created_lanes),
            "tasks_count": len(created_tasks),
            "boards": serialize_seeded_data(),
        }
