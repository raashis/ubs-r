from flask import Flask
from routes.surveillance import surveillance
app = Flask(__name__)
app.register_blueprint(trivia_bp)
app.register_blueprint(spy_network_bp)  
