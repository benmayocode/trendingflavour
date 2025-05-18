from flask import Flask
from routes.locations import bp as locations_bp
from routes.categories import bp as categories_bp
from flask_cors import CORS

app = Flask(__name__)
app.register_blueprint(locations_bp)
app.register_blueprint(categories_bp)

CORS(app, resources={r"/api/*": {"origins": "*"}})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)
