from flask import Flask
from .routes.labs import labs_bp
from .routes.session2_classlist import bp as session2_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")

    # Register blueprints
    app.register_blueprint(labs_bp, url_prefix="/labs")
    app.register_blueprint(session2_bp, url_prefix="/session2")

    @app.get("/")
    def root():
        return {"status": "running", "app": "mit261-labs"}

    @app.teardown_appcontext
    def close_mongo_client(error=None):
        from flask import g
        client = g.pop("mongo_client", None)
        if client is not None:
            client.close()

    return app
