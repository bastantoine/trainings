#!/bin/sh
export FLASK_APP=accounting.app:setup_app
.venv/bin/flask --debug run
