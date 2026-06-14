# IMPORTS
from flask import Blueprint
import src.controllers.auth as auth

# CREATE BLUEPRINT
auth_bp = Blueprint("auth", __name__)

# ROUTE: SIGN UP
@auth_bp.post("/auth/sign-up")
def sign_up():
    return auth.sign_up()

# ROUTE: SIGN IN
@auth_bp.post("/auth/sign-in")
def sign_in():
    return auth.sign_in()

# ROUTE: VERIFY 2FA
@auth_bp.post("/auth/verify-2fa")
def verify_two_factor():
    return auth.verify_two_factor()
