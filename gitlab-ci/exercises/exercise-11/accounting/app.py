from json import dumps

from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin
from flask import Flask, jsonify
from flask_swagger_ui import get_swaggerui_blueprint
from sqlalchemy import create_engine

from accounting.blueprints.expenses import expenses_blueprint
from accounting.blueprints.incomes import incomes_blueprint


def setup_app() -> Flask:
    app = Flask(__name__)
    app.config.from_pyfile("config.py")

    # Configure the connection to the DB
    MYSQL_USER = app.config['MYSQL_USER']
    MYSQL_PASSWORD = app.config['MYSQL_PASSWORD']
    MYSQL_HOST = app.config['MYSQL_HOST']
    MYSQL_DATABASE = app.config['MYSQL_DATABASE']
    conn_query = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DATABASE}"
    app.db = create_engine(conn_query)

    spec = APISpec(
        title="Accounting",
        version="1.0.0",
        openapi_version="3.0.2",
        info=dict(description="A minimal accounting API"),
        plugins=[FlaskPlugin(), MarshmallowPlugin()],
    )

    # Add blueprint with route to Swagger UI
    swaggerui_blueprint = get_swaggerui_blueprint("/docs", "/swagger.json")
    app.register_blueprint(swaggerui_blueprint)
    app.register_blueprint(incomes_blueprint)
    app.register_blueprint(expenses_blueprint)

    # Register all the endpoints in the API spec
    with app.test_request_context():
        for func in app.view_functions.values():
            spec.path(view=func)

    # Add route to serve the swagger
    @app.route("/swagger.json")
    def swagger():
        return jsonify(spec.to_dict())

    @app.cli.command("swagger")
    def generate_swagger():
        print(dumps(spec.to_dict(), indent=4))

    return app


if __name__ == "__main__":
    app = setup_app()
    app.run(debug=True, host="0.0.0.0", port=8080)
