"""
API routes for coin flip simulation - Fixed SocketIO handling
"""

from flask import Blueprint, request, jsonify
from flask_socketio import emit
import threading
import time
from src.simulation import simulator

simulation_bp = Blueprint('simulation', __name__)

# Global SocketIO instance (will be set by main.py)
_socketio = None

def register_socketio_events(socketio_instance):
    """Register SocketIO events with the provided instance."""
    global _socketio
    _socketio = socketio_instance
    
    @socketio_instance.on('connect')
    def handle_connect():
        print('Client connected')
        emit('status', {'message': 'Connected to simulation server'})
    
    @socketio_instance.on('disconnect')
    def handle_disconnect():
        print('Client disconnected')


@simulation_bp.route('/patterns', methods=['GET'])
def get_patterns():
    """Get all available pattern configurations."""
    try:
        patterns = simulator.get_available_patterns()
        return jsonify(patterns), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@simulation_bp.route('/simulation/configure', methods=['POST'])
def configure_simulation():
    """Configure simulation parameters."""
    try:
        data = request.get_json()
        pattern_name = data.get('pattern_type', '2_consecutive_tails')
        num_sessions = data.get('num_sessions', 1000)
        max_flips = data.get('max_flips_per_session', 10000)
        
        success = simulator.configure_simulation(pattern_name, num_sessions, max_flips)
        
        if success:
            return jsonify({'success': True, 'message': 'Simulation configured'}), 200
        else:
            return jsonify({'success': False, 'error': 'Invalid pattern name'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@simulation_bp.route('/simulation/start', methods=['POST'])
def start_simulation():
    """Start the simulation."""
    try:
        data = request.get_json() or {}
        
        # Configure simulation if parameters provided
        if 'pattern_type' in data:
            pattern_name = data.get('pattern_type', '2_consecutive_tails')
            num_sessions = data.get('num_sessions', 1000)
            max_flips = data.get('max_flips_per_session', 10000)
            
            config_success = simulator.configure_simulation(pattern_name, num_sessions, max_flips)
            if not config_success:
                return jsonify({'success': False, 'error': 'Invalid configuration'}), 400
        
        # Start simulation
        success = simulator.start_simulation()
        
        if success:
            # Start background simulation thread
            if _socketio:
                threading.Thread(target=run_simulation_with_updates, daemon=True).start()
            return jsonify({'success': True, 'message': 'Simulation started'}), 200
        else:
            return jsonify({'success': False, 'error': 'Failed to start simulation'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@simulation_bp.route('/simulation/stop', methods=['POST'])
def stop_simulation():
    """Stop the simulation."""
    try:
        simulator.stop_simulation()
        return jsonify({'success': True, 'message': 'Simulation stopped'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@simulation_bp.route('/simulation/reset', methods=['POST'])
def reset_simulation():
    """Reset the simulation."""
    try:
        simulator.reset_simulation()
        return jsonify({'success': True, 'message': 'Simulation reset'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@simulation_bp.route('/simulation/status', methods=['GET'])
def get_simulation_status():
    """Get current simulation status."""
    try:
        stats = simulator.get_statistics()
        return jsonify(stats), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@simulation_bp.route('/statistics', methods=['GET'])
def get_statistics():
    """Get simulation statistics."""
    try:
        stats = simulator.get_statistics()
        return jsonify(stats), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@simulation_bp.route('/sessions', methods=['GET'])
def get_sessions():
    """Get all session data."""
    try:
        sessions = simulator.get_all_sessions()
        return jsonify(sessions), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def run_simulation_with_updates():
    """Run simulation with real-time WebSocket updates."""
    global _socketio
    
    if not _socketio:
        return
    
    update_interval = 0.1  # 100ms updates
    last_stats_update = 0
    stats_update_interval = 0.5  # 500ms for statistics
    
    while simulator.is_running:
        try:
            # Step simulation
            step_result = simulator.step_simulation()
            
            # Send step updates
            if step_result['updates']:
                _socketio.emit('simulation_update', step_result)
            
            # Send statistics updates less frequently
            current_time = time.time()
            if current_time - last_stats_update >= stats_update_interval:
                stats = simulator.get_statistics()
                _socketio.emit('statistics_update', stats)
                last_stats_update = current_time
            
            # Check if simulation completed
            if step_result['status'] == 'completed':
                final_stats = simulator.get_statistics()
                _socketio.emit('simulation_completed', final_stats)
                break
            
            time.sleep(update_interval)
            
        except Exception as e:
            print(f"Error in simulation update: {e}")
            _socketio.emit('error', {'message': str(e)})
            break


@simulation_bp.route('/simulation/step', methods=['POST'])
def step_simulation():
    """Perform one step of simulation (for manual stepping)."""
    try:
        result = simulator.step_simulation()
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

