# app.py
from flask import Flask
from flask_cors import CORS  # Import CORS
from routes import routes

def create_app():
    app = Flask(__name__)
    # Allow all origins temporarily for debugging (replace with specific origin later)
    CORS(app, resources={r"/*": {"origins": "*"}})
    app.register_blueprint(routes)
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=5000)  # Ensure it runs on 5000