# IMPORTS
from datetime import datetime
from flask import current_app, jsonify, request
from peewee import IntegrityError
from src.models import User
from src.services.auth_service import (AuthConfigurationError, clear_two_factor_code, create_access_token, create_pending_two_factor_token, generate_two_factor_code, hash_password, is_valid_email, normalize_email, serialize_user, set_two_factor_code, verify_password, verify_pending_two_factor_token, verify_two_factor_code)
from src.services.mail_service import (MailConfigurationError, send_two_factor_code_email)

# FUNCTION: SIGN UP
def sign_up():

    # GET DATA FROM BODY
    data = request.get_json() or {}
    username = (data.get("username") or "").strip()
    email = normalize_email(data.get("email"))
    password = data.get("password") or ""

    # CHECK FOR USERNAME
    if not username:
        return jsonify({
            "ERROR": "USERNAME IS REQUIRED",
        }), 400

    # CHECK FOR USERNAME LENGTH
    if len(username) < 3:
        return jsonify({
            "ERROR": "USERNAME MUST BE AT LEAST 3 CHARACTERS LONG",
        }), 400

    # CHECK FOR EMAIL
    if not email:
        return jsonify({
            "ERROR": "EMAIL IS REQUIRED",
        }), 400

    # CHECK FOR VALID EMAIL
    if not is_valid_email(email):
        return jsonify({
            "ERROR": "EMAIL ADDRESS IS INVALID",
        }), 400

    # CHECK FOR PASSWORD LENGTH
    if len(password) < 8:
        return jsonify({
            "ERROR": "PASSWORD MUST BE AT LEAST 8 CHARACTERS LONG",
        }), 400

    # CHECK FOR DUPLICATES
    if User.get_or_none(User.username == username) is not None:
        return jsonify({
            "ERROR": "USERNAME IS ALREADY IN USE",
        }), 400

    # CHECK FOR ALREADY EXISTING USER
    if User.get_or_none(User.email == email) is not None:
        return jsonify({
            "ERROR": "EMAIL IS ALREADY IN USE",
        }), 400

    # TRY-CATCH BLOCK
    try:

        # CREATE USER
        user = User.create(
            username=username,
            email=email,
            password_hash=hash_password(password),
        )

    # HANDLE ERRORS
    except IntegrityError:

        # SEND ERROR RESPONSE
        return jsonify({
            "ERROR": "USERNAME OR EMAIL IS ALREADY IN USE",
        }), 400

    # SEND RESPONSE
    return jsonify({
        "MESSAGE": "USER CREATED SUCCESSFULLY",
        "user": serialize_user(user),
    }), 201


# FUNCTION: SIGN IN
def sign_in():

    # GET DATA FROM BODY
    data = request.get_json() or {}
    email = normalize_email(data.get("email"))
    password = data.get("password") or ""

    # VALIDATE INPUT
    if not email or not password:
        return jsonify({
            "ERROR": "EMAIL AND PASSWORD ARE REQUIRED",
        }), 400

    # GET USER BY EMAIL
    user = User.get_or_none(User.email == email)

    # STOP, IF USER IS UNKNOWN OR PASSWORD IS INVALID
    if user is None or not verify_password(user.password_hash, password):
        return jsonify({
            "ERROR": "INVALID EMAIL OR PASSWORD",
        }), 401

    # GENERATE NEW 2FA CODE
    two_factor_code = generate_two_factor_code()
    set_two_factor_code(user, two_factor_code)

    # TRY-CATCH BLOCK
    try:

        # SEND 2FA EMAIL
        send_two_factor_code_email(user, two_factor_code)

    # HANDLE ERRORS
    except MailConfigurationError:

        # CLEAR 2FA CODE
        clear_two_factor_code(user)

        # SEND ERROR RESPONSE
        return jsonify({
            "ERROR": "EMAIL DELIVERY IS NOT CONFIGURED",
        }), 503

    # HANDLE ERRORS
    except Exception:

        # RAISE ERROR AND CLEAR 2FA CODE
        current_app.logger.exception("Failed to send two-factor code")
        clear_two_factor_code(user)

        # SEND ERROR RESPONSE
        return jsonify({
            "ERROR": "FAILED TO SEND TWO-FACTOR CODE",
        }), 500

    # TRY-CATCH BLOCK
    try:

        # CREATE VERIFICATION TOKEN
        verification_token = create_pending_two_factor_token(user)

    # HANDLE ERRORS
    except AuthConfigurationError:

        # CLEAR 2FA CODE
        clear_two_factor_code(user)

        # SEND ERROR RESPONSE
        return jsonify({
            "ERROR": "AUTHENTICATION IS NOT CONFIGURED",
        }), 503

    # SEND RESPONSE
    return jsonify({
        "MESSAGE": "TWO-FACTOR CODE SENT",
        "email": user.email,
        "verification_token": verification_token,
    }), 200

# FUNCTION: VERIFY 2FA
def verify_two_factor():

    # GET DATA FROM BODY
    data = request.get_json() or {}
    verification_token = data.get("verification_token")
    code = (data.get("code") or "").strip()

    # CHECK FOR VERIFICATION CODE
    if not verification_token or not code:

        # SEND ERROR RESPONSE
        return jsonify({
            "ERROR": "VERIFICATION TOKEN AND CODE ARE REQUIRED",
        }), 400

    # CHECK FOR CODE LENGTH
    if len(code) != 6 or not code.isdigit():

        # SEND ERROR RESPONSE
        return jsonify({
            "ERROR": "TWO-FACTOR CODE MUST CONTAIN 6 DIGITS",
        }), 400

    # GET USER FROM PENDING TOKEN
    user = verify_pending_two_factor_token(verification_token)

    # CHECK FOR USER
    if user is None:

        # SEND ERROR RESPONSE
        return jsonify({
            "ERROR": "SIGN-IN SESSION EXPIRED OR INVALID",
        }), 401

    # CHECK FOR 2FA COEDE
    if not verify_two_factor_code(user, code):

        # CHECK FOR 2FA CODE AND EXPIRY DATE
        if user.two_factor_code_expires_at and user.two_factor_code_expires_at < datetime.utcnow():

            # CLEAR 2FA CODE
            clear_two_factor_code(user)

            # SEND ERROR RESPONSE
            return jsonify({
                "ERROR": "TWO-FACTOR CODE HAS EXPIRED",
            }), 401

        # SEND ERROR RESPONSE
        return jsonify({
            "ERROR": "INVALID TWO-FACTOR CODE",
        }), 401

    # CLEAR ONE-TIME CODE AFTER SUCCESSFUL USE
    clear_two_factor_code(user)

    # TRY-CATCH BLOCK
    try:

        #GET ACCESS TOKEN
        access_token = create_access_token(user)

    # HANDLE ERRORS
    except AuthConfigurationError:

        # SEND ERROR RESPONSE
        return jsonify({
            "ERROR": "AUTHENTICATION IS NOT CONFIGURED",
        }), 503

    # SEND RESPONSE
    return jsonify({
        "MESSAGE": "SIGNED IN SUCCESSFULLY",
        "token": access_token,
        "user": serialize_user(user),
    }), 200
