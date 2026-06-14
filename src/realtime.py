# IMPORTS
import json
from threading import Lock
from flask import g, has_request_context, request
from flask_sock import Sock
from src.services.auth_service import verify_access_token

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

# FUNCTION: GET CURRENT BOARD EVENT ACTOR
def get_board_event_actor():

    # STOP, IF THERE IS NO ACTIVE REQUEST CONTEXT
    if not has_request_context():
        return None

    # GET CURRENT USER
    current_user = getattr(g, "current_user", None)

    # STOP, IF NO USER IS AVAILABLE
    if current_user is None:
        return None

    # RETURN ACTOR PAYLOAD
    return {
        "id": current_user.id,
        "username": current_user.username,
    }

# FUNCTION: GET CURRENT BOARD EVENT ACTOR NAME
def get_board_event_actor_name():

    # GET ACTOR
    actor = get_board_event_actor()

    # RETURN USERNAME OR FALLBACK
    return actor["username"] if actor else "Someone"

# FUNCTION: BROADCAST BOARD EVENT
def broadcast_board_event(board_id, event_type, payload=None, excluded_client_id=None):

    # COPY PAYLOAD SO CALLERS KEEP OWNERSHIP
    payload = dict(payload or {})

    # INCLUDE ACTOR METADATA WHEN AVAILABLE
    actor = get_board_event_actor()

    # ADD ACTOR TO PAYLOAD IF AVAILABLE
    if actor and "actor" not in payload:
        payload["actor"] = actor

    # BUILD MESSAGE
    message = json.dumps({
        "type": event_type,
        "board_id": board_id,
        "payload": payload,
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

        # TRY-CATCH BLOCK
        try:

            # SEND MESSAGE
            subscriber["ws"].send(message)

        # HANDLE ERRORS
        except Exception:

            # SAVE FAILED WEBSOCKET
            stale_subscribers.append(subscriber["ws"])

    # REMOVE STALE SUBSCRIBERS
    for ws in stale_subscribers:
        unregister_board_subscriber(board_id, ws)

# FUNCTION: BOARD UPDATES
@sock.route("/ws/boards/<int:board_id>")
def board_updates(ws, board_id):

    # REQUIRE A VALID ACCESS TOKEN BEFORE SUBSCRIBING
    if verify_access_token(request.args.get("token")) is None:

        # TRY-CATCH BLOCK
        try:

            # CLOSE CONNECTION
            ws.close()

        # HANDLE ERRORS
        except Exception:

            # PASS ALL
            pass

        # BREAK
        return

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
