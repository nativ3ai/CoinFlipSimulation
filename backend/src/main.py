"""
Flask main application - Fixed SocketIO import issue
"""
import os
import sys
# DON'T CHANGE THIS PATH
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'coin_flip_secret_key_2024'
    
    # Enable CORS for all domains
    CORS(app, origins="*")
    
    # Initialize SocketIO with CORS enabled
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
    
    # Import and register routes after socketio is created
    from routes.simulation import simulation_bp, register_socketio_events
    app.register_blueprint(simulation_bp, url_prefix='/api')
    
    # Register SocketIO events
    register_socketio_events(socketio)
    
    return app, socketio

if __name__ == '__main__':
    app, socketio = create_app()
    # Bind to all interfaces for Docker
    socketio.run(app, host='0.0.0.0', port=5000, debug=False, allow_unsafe_werkzeug=True)

