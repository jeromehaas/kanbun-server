# IMPORTS
from flask import Flask

# SETUP APP
app = Flask(__name__)

# ROUTE HELLO-WORLD
@app.route('/')
def hello_world():
    return "<p>Hello, World!</p>"