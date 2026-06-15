import sys
import os
import traceback

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

try:
    from app import app
except Exception as e:
    tb = traceback.format_exc()
    from flask import Flask, jsonify
    
    # Fallback Flask app to display the traceback if initialization fails
    app = Flask(__name__)
    
    @app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE'])
    @app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
    def catch_all(path):
        return jsonify({
            "error": "Backend initialization failed",
            "exception": str(e),
            "traceback": tb.split('\n')
        }), 500
