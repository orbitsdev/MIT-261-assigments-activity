from flask import Flask, after_this_request
from .routes.labs import labs_bp
from .routes.session2_classlist import bp as session2_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")
    
    @app.after_request
    def add_cache_control(response):
        # Disable caching for HTML, CSS, and JS files
        if response.mimetype in ['text/html', 'text/css', 'application/javascript']:
            response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
        return response

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
