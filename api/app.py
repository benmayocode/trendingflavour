from flask import Flask
from routes.locations import bp as locations_bp
from routes.categories import bp as categories_bp

app = Flask(__name__)
app.register_blueprint(locations_bp)
app.register_blueprint(categories_bp)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)
