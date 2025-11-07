from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from database import db
import os

def create_app():
    app = Flask(__name__)
    CORS(app)

    # --- DATABASE CONFIG ---
    DATABASE_URL = os.getenv("MYSQL_URL") or os.getenv("DATABASE_URL")

    # Convert mysql:// to mysql+pymysql:// (Railway fix)
    if DATABASE_URL and DATABASE_URL.startswith("mysql://"):
        DATABASE_URL = DATABASE_URL.replace("mysql://", "mysql+pymysql://", 1)

    # Fallback to SQLite (local development)
    if not DATABASE_URL:
        DATABASE_URL = "sqlite:///data.db"

    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # JWT Key
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "dev-secret-key")

    # Init Extensions
    db.init_app(app)
    JWTManager(app)

    # Blueprints
    from routes.auth import bp as auth_bp
    from routes.habits import bp as habits_bp
    from routes.moods import bp as moods_bp
    from routes.journals import bp as journals_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(habits_bp)
    app.register_blueprint(moods_bp)
    app.register_blueprint(journals_bp)

    @app.route("/")
    def home():
        return {"message": "MyPal API Running Successfully 🚀"}

    @app.route("/health")
    def health():
        try:
            db.session.execute(db.text('SELECT 1'))
            return {"database": "connected", "status": "ok"}
        except:
            return {"database": "disconnected", "status": "error"}

    return app


app = create_app()

@app.before_first_request
def create_tables():
    db.create_all()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)
