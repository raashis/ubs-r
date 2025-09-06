from flask import Flask
from routes.surveillance import surveillance  # This imports the Blueprint

app = Flask(__name__)
app.register_blueprint(surveillance)
