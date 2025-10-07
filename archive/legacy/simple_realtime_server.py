#!/usr/bin/env python3
"""
FISO Real-Time Server - Simplified Version
WebSocket server without eventlet complications
"""

import os
import sys
import logging
import json
import time
import threading
from datetime import datetime, timezone
from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS

# Add paths for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'security'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'predictor'))

def setup_logging():
    """Configure logging"""
    os.makedirs('logs', exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(f'logs/realtime_{datetime.now().strftime("%Y%m%d")}.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'fiso-realtime-secret-2025'

# Enable CORS
CORS(app, origins=['http://localhost:3000', 'http://127.0.0.1:3000'])

# Initialize SocketIO with threading instead of eventlet
socketio = SocketIO(
    app, 
    cors_allowed_origins=['http://localhost:3000', 'http://127.0.0.1:3000'],
    async_mode='threading',  # Use threading instead of eventlet
    logger=False,
    engineio_logger=False
)

# Global variables for tracking connections and data
connected_clients = set()
streaming_data = {}
report_cache = {}

# Try to import AI engines (optional)
try:
    from lightweight_ai_engine import LightweightAIEngine
    ai_engine = LightweightAIEngine()
    logger.info("AI Engine imported successfully")
except ImportError as e:
    logger.warning(f"AI engines not available: {str(e)}")
    ai_engine = None

# Try to import executive reporting (optional)
try:
    from executive_reporting import ExecutiveReporting
    executive_reporting = ExecutiveReporting()
    logger.info("Executive Reporting imported successfully")
except ImportError as e:
    logger.warning(f"Executive reporting not available: {str(e)}")
    executive_reporting = None

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'service': 'FISO Real-Time Server',
        'version': '1.0.0',
        'websocket_enabled': True,
        'connected_clients': len(connected_clients),
        'ai_engine_available': ai_engine is not None,
        'executive_reporting_available': executive_reporting is not None
    })

@app.route('/api/reports/list')
def list_reports():
    """List available reports"""
    try:
        # Mock reports for now
        reports = [
            {
                'id': f'report_{int(time.time())}_1',
                'name': 'Monthly Cost Summary',
                'type': 'cost_summary',
                'created_at': datetime.utcnow().isoformat() + 'Z',
                'status': 'completed'
            },
            {
                'id': f'report_{int(time.time())}_2',
                'name': 'Optimization Recommendations',
                'type': 'optimization',
                'created_at': datetime.utcnow().isoformat() + 'Z',
                'status': 'completed'
            }
        ]
        
        return jsonify({
            'reports': reports,
            'total': len(reports)
        })
    except Exception as e:
        logger.error(f"Error listing reports: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/reports/generate', methods=['POST'])
def generate_report():
    """Generate a new report"""
    try:
        data = request.get_json() or {}
        report_type = data.get('type', 'cost_summary')
        
        # Generate mock report
        report_id = f'report_{int(time.time())}_{report_type}'
        
        # Simulate report generation
        def generate_async():
            time.sleep(2)  # Simulate processing time
            report_cache[report_id] = {
                'id': report_id,
                'type': report_type,
                'status': 'generated',
                'created_at': datetime.utcnow().isoformat() + 'Z',
                'data': {
                    'summary': f'Generated {report_type} report',
                    'metrics': {
                        'total_cost': 1234.56,
                        'savings': 234.78,
                        'efficiency': 0.82
                    }
                }
            }
            
            # Notify connected clients
            socketio.emit('report_generated', {
                'report_id': report_id,
                'type': report_type,
                'status': 'completed'
            })
        
        # Start generation in background
        thread = threading.Thread(target=generate_async)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'report_id': report_id,
            'status': 'processing',
            'estimated_completion': 30  # seconds
        })
        
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        return jsonify({'error': str(e)}), 500

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    client_id = request.sid
    connected_clients.add(client_id)
    logger.info(f"Client connected: {client_id} (Total: {len(connected_clients)})")
    
    emit('connection_confirmed', {
        'client_id': client_id,
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'message': 'Connected to FISO Real-Time Server'
    })

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    client_id = request.sid
    connected_clients.discard(client_id)
    logger.info(f"Client disconnected: {client_id} (Total: {len(connected_clients)})")

@socketio.on('subscribe')
def handle_subscribe(data):
    """Handle subscription to data channels"""
    try:
        channel = data.get('channel', 'general')
        client_id = request.sid
        
        # Join the specified room/channel
        join_room(channel)
        
        logger.info(f"Client {client_id} subscribed to channel: {channel}")
        
        emit('subscription_confirmed', {
            'channel': channel,
            'client_id': client_id,
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        })
        
        # Send initial data if available
        if channel == 'cost_updates':
            emit('cost_update', {
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'aws_cost': 1234.56,
                'azure_cost': 567.89,
                'gcp_cost': 234.12,
                'total_cost': 2036.57,
                'change_percent': -2.3
            })
            
    except Exception as e:
        logger.error(f"Error handling subscription: {str(e)}")
        emit('error', {'message': str(e)})

@socketio.on('unsubscribe')
def handle_unsubscribe(data):
    """Handle unsubscription from data channels"""
    try:
        channel = data.get('channel', 'general')
        client_id = request.sid
        
        # Leave the specified room/channel
        leave_room(channel)
        
        logger.info(f"Client {client_id} unsubscribed from channel: {channel}")
        
        emit('unsubscription_confirmed', {
            'channel': channel,
            'client_id': client_id,
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        })
        
    except Exception as e:
        logger.error(f"Error handling unsubscription: {str(e)}")
        emit('error', {'message': str(e)})

def broadcast_updates():
    """Background thread to broadcast periodic updates"""
    import random
    
    while True:
        try:
            if connected_clients:
                # Generate mock real-time data
                cost_update = {
                    'timestamp': datetime.utcnow().isoformat() + 'Z',
                    'aws_cost': round(1000 + random.uniform(-100, 100), 2),
                    'azure_cost': round(500 + random.uniform(-50, 50), 2),
                    'gcp_cost': round(200 + random.uniform(-20, 20), 2),
                    'change_percent': round(random.uniform(-5, 5), 1)
                }
                cost_update['total_cost'] = cost_update['aws_cost'] + cost_update['azure_cost'] + cost_update['gcp_cost']
                
                # Broadcast to cost_updates channel
                socketio.emit('cost_update', cost_update, room='cost_updates')
                
                # Send heartbeat to all clients
                socketio.emit('heartbeat', {
                    'timestamp': datetime.utcnow().isoformat() + 'Z',
                    'server_status': 'healthy',
                    'connected_clients': len(connected_clients)
                })
                
            time.sleep(30)  # Update every 30 seconds
            
        except Exception as e:
            logger.error(f"Error in broadcast updates: {str(e)}")
            time.sleep(60)  # Wait longer on error

def main():
    """Main function to start the real-time server"""
    logger.info("Starting FISO Real-Time Server with WebSocket Support...")
    
    # Start background update thread
    update_thread = threading.Thread(target=broadcast_updates)
    update_thread.daemon = True
    update_thread.start()
    
    logger.info("Real-Time Server Configuration:")
    logger.info("   • Host: 0.0.0.0")
    logger.info("   • Port: 5001")
    logger.info("   • WebSocket: Enabled")
    logger.info("   • Real-time Streaming: Active")
    logger.info("=" * 70)
    logger.info("FISO Enterprise Intelligence Platform - REAL-TIME MODE")
    logger.info("=" * 70)
    
    # Start the server
    try:
        socketio.run(
            app,
            host='0.0.0.0',
            port=5001,
            debug=False,
            use_reloader=False
        )
    except KeyboardInterrupt:
        logger.info("Real-time server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {str(e)}")

if __name__ == '__main__':
    main()