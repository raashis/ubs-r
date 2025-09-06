from flask import Flask
from routes.surveillance import surveillance  # ✅ This matches the blueprint name

app = Flask(__name__)
app.register_blueprint(surveillance)  # ✅ Register it
