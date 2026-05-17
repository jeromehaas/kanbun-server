# IMPORTS
import os
from flask import jsonify
from src.services.seed_service import run_seed
from src.database import reset_tables

# FUNCTION: CREATE
def create():

    # GET ENVIRONMENT
    app_env = os.getenv("APP_ENV", "").lower()

    # CHECK FOR DEV ENVIRONMENT
    if app_env != "dev":
        return jsonify({
            "ERROR": "SEED ROUTE IS ONLY AVAILABLE IN DEV"
        }), 403

    # TRY-CATCH BLOCK
    try:

        # RESET TABLES
        reset_tables()

        # RUN SEED SERVICE
        run_seed()

    # HANDLE VALUE ERRORS
    except ValueError as error:
        return jsonify({
            "ERROR": str(error)
        }), 400

    # HANDLE ERRORS
    except Exception as error:
        return jsonify({
            "ERROR": "SEED FAILED",
        }), 500

    # SEND RESPONSE
    return jsonify({
        "MESSAGE": "DATABASE SEEDED SUCCESSFULLY",
    }), 200