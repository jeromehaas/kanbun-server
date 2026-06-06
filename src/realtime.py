# IMPORTS
import json
from threading import Lock
from flask_sock import Sock

# SETUP SOCKETS AND SUBSCRIBERS
sock = Sock()
board_subscribers = {}
board_subscribers_lock = Lock()

# FUNCTION: INIT REALTIME
def init_realtime(app):

    # INIT SOCKETS
    sock.init_app(app)

# FUNCTION: REGISTER BOARD SUBSCRIBER
def register_board_subscriber(board_id, ws):

    # LOCK SUBSCRIBER REGISTRY
    with board_subscribers_lock:

        # GET OR CREATE BOARD SUBSCRIBERS
        subscribers = board_subscribers.setdefault(board_id, [])

        # ADD SUBSCRIBER ENTRY
        subscribers.append({
            "ws": ws,
            "client_id": None,
        })

# FUNCTION: UPDATE BOARD SUBSCRIBER CLIENT ID
def update_board_subscriber_client_id(board_id, ws, client_id):

    # LOCK SUBSCRIBER REGISTRY
    with board_subscribers_lock:

        # LOOP OVER BOARD SUBSCRIBERS
        for subscriber in board_subscribers.get(board_id, []):

            # MATCH SUBSCRIBER BY WEBSOCKET
            if subscriber["ws"] is ws:

                # SAVE CLIENT ID
                subscriber["client_id"] = client_id
                break


# FUNCTION: UNREGISTER BOARD SUBSCRIBER
def unregister_board_subscriber(board_id, ws):

    # LOCK SUBSCRIBER REGISTRY
    with board_subscribers_lock:

        # GET CURRENT SUBSCRIBERS
        subscribers = board_subscribers.get(board_id, [])

        # REMOVE MATCHING WEBSOCKET
        subscribers = [subscriber for subscriber in subscribers if subscriber["ws"] is not ws]

        # KEEP OR REMOVE BOARD SUBSCRIBERS
        if subscribers:
            board_subscribers[board_id] = subscribers
        else:
            board_subscribers.pop(board_id, None)

# FUNCTION: BROADCAST BOARD EVENT
def broadcast_board_event(board_id, event_type, payload=None, excluded_client_id=None):

    # BUILD MESSAGE
    message = json.dumps({
        "type": event_type,
        "board_id": board_id,
        "payload": payload or {},
        "source_client_id": excluded_client_id,
    })

    # LOCK SUBSCRIBER REGISTRY
    with board_subscribers_lock:

        # COPY CURRENT SUBSCRIBERS
        subscribers = list(board_subscribers.get(board_id, []))

    # TRACK STALE SUBSCRIBERS
    stale_subscribers = []

    # LOOP OVER SUBSCRIBERS
    for subscriber in subscribers:

        # SKIP THE SOURCE CLIENT
        if excluded_client_id and subscriber.get("client_id") == excluded_client_id:
            continue

        # TRY TO SEND MESSAGE
        try:

            # SEND MESSAGE
            subscriber["ws"].send(message)

        # TRACK SEND FAILURES
        except Exception:

            # SAVE FAILED WEBSOCKET
            stale_subscribers.append(subscriber["ws"])

    # REMOVE STALE SUBSCRIBERS
    for ws in stale_subscribers:
        unregister_board_subscriber(board_id, ws)


# FUNCTION: BOARD UPDATES
@sock.route("/ws/boards/<int:board_id>")
def board_updates(ws, board_id):

    # REGISTER SUBSCRIBER
    register_board_subscriber(board_id, ws)

    # TRY-CATCH BLOCK
    try:

        # KEEP CONNECTION OPEN
        while True:

            # RECEIVE MESSAGE
            raw_message = ws.receive()

            # STOP ON CLOSED CONNECTION
            if raw_message is None:
                break

            try:

                # PARSE JSON MESSAGE
                message = json.loads(raw_message)
            except (TypeError, ValueError):

                # IGNORE INVALID MESSAGES
                continue

            # SAVE CLIENT ID FROM HELLO MESSAGE
            if message.get("type") == "hello":
                update_board_subscriber_client_id(board_id, ws, message.get("client_id"))

    # FINALLY
    finally:

        # UNREGISTER SUBSCRIBER
        unregister_board_subscriber(board_id, ws)
