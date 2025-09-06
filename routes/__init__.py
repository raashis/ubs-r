from flask import Flask
from routes.trivia import trivia_bp

app = Flask(__name__)
app.register_blueprint(trivia_bp)
