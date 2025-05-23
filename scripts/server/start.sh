#!/bin/bash

# Navigate to the server directory
cd "$(dirname "$0")"

# Set environment variables
export FLASK_APP=main.py
export FLASK_ENV=production

# Start the Flask app with Gunicorn
gunicorn -b 0.0.0.0:$PORT main:app
