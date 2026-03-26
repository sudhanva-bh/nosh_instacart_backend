"""
main.py
-------
Minimal application factory showing how to register the Instacart Blueprint.

Your team can copy this pattern into your real entry-point or expand the
create_app() factory as needed.
"""

from flask import Flask
from dotenv import load_dotenv

load_dotenv()

from instacart_routes import instacart_bp 


def create_app() -> Flask:
    """Application factory."""
    app = Flask(__name__)

    app.register_blueprint(instacart_bp)

    return app

if __name__ == "__main__":
    application = create_app()
    application.run(debug=True, port=5000)
