from flask import Flask
from routes.locations import bp as locations_bp
from routes.categories import bp as categories_bp
from routes.trends import bp as trends_bp
from routes.locations_cosmos import bp as locations_cosmos_bp
from routes.trends_cosmos import bp as trends_cosmos_bp
from flask_cors import CORS

app = Flask(__name__)
app.register_blueprint(locations_bp)
app.register_blueprint(categories_bp)
app.register_blueprint(trends_bp)

app.register_blueprint(locations_cosmos_bp)
app.register_blueprint(trends_cosmos_bp)

CORS(app, resources={r"/api/*": {"origins": "*"}})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)
