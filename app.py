from flask import Flask

from api_channels import api_channels
from database import db_session

app = Flask(__name__)
app.register_blueprint(api_channels)


@app.teardown_appcontext
def close_session(exception=None):
    db_session.remove()
