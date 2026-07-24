import os
from dotenv import load_dotenv

# Base directory of the backend folder
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Load the environment variables from .env if present.
# Note: Existing environment variables (e.g., set by tests or container runtime)
# are not overwritten, allowing dynamic configuration.
load_dotenv(os.path.join(BASE_DIR, ".env"))

class Config:
    FLASK_ENV = os.environ.get("FLASK_ENV", "development")
    FLASK_DEBUG = os.environ.get("FLASK_DEBUG", "True").lower() in ("true", "1", "yes")
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production-12345")
    PORT = int(os.environ.get("PORT", 5000))

    # Resolve database path dynamically
    db_name = os.environ.get("DATABASE_PATH", "campus_events.db")
    if os.path.isabs(db_name):
        DATABASE_PATH = db_name
    else:
        DATABASE_PATH = os.path.abspath(os.path.join(BASE_DIR, db_name))
