from flask import Flask
from routes.trivia import trivia_bp
from routes.spy_network import spy_network_bp  
app = Flask(__name__)
app.register_blueprint(trivia_bp)
app.register_blueprint(spy_network_bp)  
