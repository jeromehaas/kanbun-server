# [Server] Kanbun 

![Python](https://img.shields.io/badge/Python-3.x-blue)
![Flask](https://img.shields.io/badge/Flask-Backend-black)

Kanbun Server is the backend for the Kanbun project, built with Python and Flask. It handles the core business logic, data management, and API endpoints that power the Kanbun ecosystem. The server acts as the central source of truth for boards, tasks, and workflow state used by the TUI and other future clients.

## Requirements
- Python
- A reachable PostgreSQL database
- A PostgreSQL user with permission to create tables in the target database/schema

## Installation
Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install dependencies:
```bash
pip install -r requirements.txt
```

## Environment variables
Create a `.env` file in the project root:

```env
# FLASK
FLASK_APP=app:create_app
FLASK_DEBUG=1
FLASK_RUN_PORT=5001

# APP
APP_ENV=dev

# DATABASE
DATABASE_USER=
DATABASE_PASSWORD=
DATABASE_HOST=
DATABASE_PORT=
DATABASE_DB_NAME=
```

## Run the server
In the root of the application, run this command:

```bash
flask --app src/app.py run -p 5001
```
