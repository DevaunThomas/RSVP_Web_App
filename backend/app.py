from flask import Flask, jsonify
from flask_cors import CORS

from config import Config
from database import DatabaseHelper
from routes.event_routes import event_routes
from routes.rsvp_routes import rsvp_routes
from routes.user_routes import user_routes


def create_app() -> Flask:
    app = Flask(__name__)

    # Apply configuration settings
    app.config.from_object(Config)

    # Allows the frontend to send requests to this backend.
    CORS(app)

    DatabaseHelper.init_db()

    app.register_blueprint(user_routes, url_prefix="/api")
    app.register_blueprint(event_routes, url_prefix="/api")
    app.register_blueprint(rsvp_routes, url_prefix="/api")

    @app.get("/")
    def home():
        return jsonify({
            "message": "Campus Event RSVP API is running"
        }), 200

    @app.errorhandler(404)
    def not_found(_error):
        return jsonify({
            "error": "Route not found"
        }), 404

    @app.errorhandler(500)
    def internal_error(_error):
        return jsonify({
            "error": "An internal server error occurred"
        }), 500

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=Config.FLASK_DEBUG, port=Config.PORT)