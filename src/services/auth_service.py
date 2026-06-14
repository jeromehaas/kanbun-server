# IMPORTS
import os
import re
import secrets
from datetime import datetime, timedelta
from flask import g, jsonify, request
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from werkzeug.security import check_password_hash, generate_password_hash
from src.models import User

# SETUP CONSTANTS
ACCESS_TOKEN_MAX_AGE_SECONDS = 60 * 60 * 24 * 7
PENDING_2FA_MAX_AGE_SECONDS = 60 * 10
TWO_FACTOR_CODE_TTL_MINUTES = 10
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
DEV_AUTH_SECRET_KEY = "dev-auth-secret-key-change-me"

# CLASS: AUTH CONFIGURATION ERROR
class AuthConfigurationError(RuntimeError):
    pass

# FUNCTION: GET AUTH SECRET KEY
def get_auth_secret_key():

    # GET SECRET KEY
    secret_key = os.getenv("AUTH_SECRET_KEY")

    # RETURN KEY IF AVAILABLE
    if secret_key:
        return secret_key

    # ALLOW A DEV FALLBACK TO KEEP LOCAL SETUP SIMPLE
    if os.getenv("APP_ENV", "").lower() == "dev":
        return DEV_AUTH_SECRET_KEY

    # STOP, IF NO SECRET KEY IS AVAILABLE
    raise AuthConfigurationError("AUTH_SECRET_KEY IS NOT CONFIGURED")

# FUNCTION: GET TOKEN SERIALIZER
def get_token_serializer(salt):
    return URLSafeTimedSerializer(get_auth_secret_key(), salt=salt)

# FUNCTION: NORMALIZE EMAIL
def normalize_email(email):
    return (email or "").strip().lower()

# FUNCTION: VALIDATE EMAIL
def is_valid_email(email):
    return bool(EMAIL_PATTERN.match(normalize_email(email)))

# FUNCTION: HASH PASSWORD
def hash_password(password):
    return generate_password_hash(password)

# FUNCTION: CHECK PASSWORD
def verify_password(password_hash, password):
    return check_password_hash(password_hash, password or "")

# FUNCTION: GENERATE 2FA CODE
def generate_two_factor_code():
    return f"{secrets.randbelow(1_000_000):06d}"

# FUNCTION: SAVE 2FA CODE
def set_two_factor_code(user, code):

    # SAVE HASHED CODE AND EXPIRATION
    user.two_factor_code_hash = generate_password_hash(code)
    user.two_factor_code_expires_at = datetime.utcnow() + timedelta(minutes=TWO_FACTOR_CODE_TTL_MINUTES)
    user.save(only=[User.two_factor_code_hash, User.two_factor_code_expires_at])

# FUNCTION: CLEAR 2FA CODE
def clear_two_factor_code(user):

    # REMOVE ACTIVE 2FA CHALLENGE
    user.two_factor_code_hash = None
    user.two_factor_code_expires_at = None
    user.save(only=[User.two_factor_code_hash, User.two_factor_code_expires_at])

# FUNCTION: VERIFY 2FA CODE
def verify_two_factor_code(user, code):

    # STOP, IF NO ACTIVE CODE EXISTS
    if not user.two_factor_code_hash or not user.two_factor_code_expires_at:
        return False

    # STOP, IF CODE HAS EXPIRED
    if user.two_factor_code_expires_at < datetime.utcnow():
        return False

    # VERIFY CODE AGAINST HASH
    return check_password_hash(user.two_factor_code_hash, (code or "").strip())


# FUNCTION: CREATE ACCESS TOKEN
def create_access_token(user):

    # DUMP USER ID
    return get_token_serializer("kanbun-access-token").dumps({
        "user_id": user.id,
    })

# FUNCTION: VERIFY ACCESS TOKEN
def verify_access_token(token):

    # STOP, IF NO TOKEN IS AVAILABLE
    if not token:
        return None

    # TRY-CATCH BLOCK
    try:

        # GET TOKEN DATA
        token_data = get_token_serializer("kanbun-access-token").loads(
            token,
            max_age=ACCESS_TOKEN_MAX_AGE_SECONDS,
        )

    # HANDLE ERRORS
    except (BadSignature, SignatureExpired):
        return None

    # GET USER FROM TOKEN
    user_id = token_data.get("user_id")

    # STOP, IF NO USER ID EXISTS
    if not user_id:
        return None

    # RETURN USER
    return User.get_or_none(User.id == user_id)

# FUNCTION: CREATE PENDING 2FA TOKEN
def create_pending_two_factor_token(user):

    # RETURN TOKEN
    return get_token_serializer("kanbun-pending-2fa-token").dumps({
        "user_id": user.id,
    })

# FUNCTION: VERIFY PENDING 2FA TOKEN
def verify_pending_two_factor_token(token):

    # STOP, IF NO TOKEN IS AVAILABLE
    if not token:
        return None

    # TRY-CATCH BLOCK
    try:

        # GET TOKEN
        token_data = get_token_serializer("kanbun-pending-2fa-token").loads(
            token,
            max_age=PENDING_2FA_MAX_AGE_SECONDS,
        )

    # HANDLE ERRORS
    except (BadSignature, SignatureExpired):
        return None

    # GET USER ID
    user_id = token_data.get("user_id")

    # STOP, IF NO USER ID EXISTS
    if not user_id:
        return None

    # RETURN USER
    return User.get_or_none(User.id == user_id)


# FUNCTION: SERIALIZE USER
def serialize_user(user):

    # RETURN UDER OBJECT
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
    }

# FUNCTION: GET BEARER TOKEN
def get_bearer_token():

    # GET AUTHORIZATION HEADER
    authorization_header = request.headers.get("Authorization", "")
    scheme, _, token = authorization_header.partition(" ")

    # STOP, IF HEADER IS INVALID
    if scheme.lower() != "bearer" or not token:
        return None

    # RETURN CLEAN TOKEN
    return token.strip()


# FUNCTION: REQUIRE HTTP AUTH
def require_http_auth():

    # GET USER FROM ACCESS TOKEN
    user = verify_access_token(get_bearer_token())

    # CHECK FOR USER
    if user is None:

        # SEND ERROR RESPONSE
        return jsonify({
            "ERROR": "AUTHENTICATION REQUIRED",
        }), 401

    # SAVE CURRENT USER
    g.current_user = user
    return None

