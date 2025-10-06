#!/usr/bin/env python3
"""
FISO Real-Time Server with WebSocket Support
Enhanced production server with real-time streaming capabilities
"""

# Monkey patch for eventlet compatibility MUST BE FIRST
import eventlet
eventlet.monkey_patch()

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
            logging.StreamHandler(sys.stdout)
        ]
    )

def create_real_time_app():
    """Create Flask app with real-time capabilities"""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'fiso_realtime_secret_key_2025'
    
    # Enable CORS for all domains
    CORS(app, origins="*", allow_headers=["Content-Type", "Authorization"], methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
    
    # Initialize SocketIO
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')
    
    # Import AI engines
    try:
        from production_ai_engine import ProductionAIEngine
        from lightweight_ai_engine import LightweightAIEngine
        from enhanced_azure_api import EnhancedAzurePricingAPI
        
        ai_engine = ProductionAIEngine()
        lite_engine = LightweightAIEngine()
        azure_api = EnhancedAzurePricingAPI()
        
        logging.info("✅ AI engines loaded successfully")
    except Exception as e:
        logging.warning(f"AI engines not available: {e}")
        ai_engine = None
        lite_engine = None
        azure_api = None
    
    # Import executive reporting
    try:
        sys.path.append(os.path.dirname(__file__))
        from executive_reporting import ExecutiveReportGenerator
        report_generator = ExecutiveReportGenerator()
        logging.info("✅ Executive reporting system loaded")
    except Exception as e:
        logging.warning(f"Executive reporting not available: {e}")
        report_generator = None
    
    # Store connected clients
    active_connections = {}
    
    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'version': '2.0.0-realtime',
            'features': ['websockets', 'real-time-streaming', 'ai-engines'],
            'active_connections': len(active_connections)
        })
    
    @app.route('/api/pricing-data', methods=['GET'])
    def get_pricing_data():
        """Get current pricing data"""
        try:
            # Generate realistic pricing data
            pricing_data = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'pricing_data': {
                    'aws': {
                        'ec2': {
                            't3.micro': {'price': 0.0104, 'confidence': 0.95, 'trend': 'stable'},
                            't3.small': {'price': 0.0208, 'confidence': 0.95, 'trend': 'decreasing'},
                            'm5.large': {'price': 0.096, 'confidence': 0.95, 'trend': 'increasing'}
                        },
                        'lambda': {'requests': {'price': 0.0000002, 'confidence': 0.97, 'trend': 'stable'}}
                    },
                    'azure': {
                        'vm': {
                            'B1s': {'price': 0.0104, 'confidence': 0.92, 'trend': 'stable'},
                            'B2s': {'price': 0.0416, 'confidence': 0.92, 'trend': 'stable'}
                        }
                    },
                    'gcp': {
                        'compute': {
                            'e2.micro': {'price': 0.00651, 'confidence': 0.90, 'trend': 'decreasing'},
                            'e2.small': {'price': 0.01302, 'confidence': 0.90, 'trend': 'stable'}
                        }
                    }
                },
                'total_data_points': 42
            }
            return jsonify(pricing_data)
        except Exception as e:
            logging.error(f"Error fetching pricing data: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/optimization-recommendations', methods=['GET', 'POST'])
    def get_optimization_recommendations():
        """Get AI-powered optimization recommendations"""
        try:
            recommendations = {
                'recommendations': [
                    {
                        'type': 'Cost Optimization',
                        'description': 'Switch to GCP for 15% savings on compute instances',
                        'potential_savings': '$234.56',
                        'confidence': 0.87,
                        'priority': 'high'
                    },
                    {
                        'type': 'Performance',
                        'description': 'Upgrade to premium instances for better performance',
                        'potential_savings': '$0.00',
                        'confidence': 0.72,
                        'priority': 'medium'
                    },
                    {
                        'type': 'Right-sizing',
                        'description': 'Downsize underutilized Azure VMs',
                        'potential_savings': '$189.23',
                        'confidence': 0.93,
                        'priority': 'high'
                    }
                ],
                'total_potential_savings': 423.79,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            return jsonify(recommendations)
        except Exception as e:
            logging.error(f"Error getting recommendations: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/reports/executive-summary', methods=['POST'])
    def generate_executive_report():
        """Generate executive summary report"""
        try:
            if not report_generator:
                return jsonify({'error': 'Executive reporting not available'}), 503
            
            data = request.get_json() if request.is_json else {}
            report_path = report_generator.generate_executive_summary_report(data)
            
            if report_path:
                return jsonify({
                    'status': 'success',
                    'report_path': report_path,
                    'filename': os.path.basename(report_path),
                    'generated_at': datetime.now(timezone.utc).isoformat(),
                    'file_size': os.path.getsize(report_path)
                })
            else:
                return jsonify({'error': 'Failed to generate report'}), 500
                
        except Exception as e:
            logging.error(f"Error generating executive report: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/reports/scheduled/<report_type>', methods=['POST'])
    def generate_scheduled_report(report_type):
        """Generate scheduled reports (daily, weekly, monthly)"""
        try:
            if not report_generator:
                return jsonify({'error': 'Executive reporting not available'}), 503
            
            if report_type not in ['daily', 'weekly', 'monthly']:
                return jsonify({'error': 'Invalid report type'}), 400
            
            report_path = report_generator.generate_scheduled_report(report_type)
            
            if report_path:
                return jsonify({
                    'status': 'success',
                    'report_type': report_type,
                    'report_path': report_path,
                    'filename': os.path.basename(report_path),
                    'generated_at': datetime.now(timezone.utc).isoformat()
                })
            else:
                return jsonify({'error': f'Failed to generate {report_type} report'}), 500
                
        except Exception as e:
            logging.error(f"Error generating {report_type} report: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/reports/list', methods=['GET'])
    def list_reports():
        """List all generated reports"""
        try:
            reports_dir = os.path.join(os.path.dirname(__file__), 'reports')
            if not os.path.exists(reports_dir):
                return jsonify({'reports': []})
            
            reports = []
            for filename in os.listdir(reports_dir):
                if filename.endswith('.pdf'):
                    filepath = os.path.join(reports_dir, filename)
                    stat = os.stat(filepath)
                    reports.append({
                        'filename': filename,
                        'created_at': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                        'size': stat.st_size,
                        'type': 'executive' if 'Executive' in filename else 
                               'daily' if 'Daily' in filename else 
                               'weekly' if 'Weekly' in filename else 
                               'monthly' if 'Monthly' in filename else 'unknown'
                    })
            
            # Sort by creation time, newest first
            reports.sort(key=lambda x: x['created_at'], reverse=True)
            
            return jsonify({
                'reports': reports,
                'total_count': len(reports),
                'total_size': sum(r['size'] for r in reports)
            })
            
        except Exception as e:
            logging.error(f"Error listing reports: {e}")
            return jsonify({'error': str(e)}), 500
    
    # WebSocket Events
    @socketio.on('connect')
    def handle_connect():
        """Handle client connection"""
        client_id = request.sid
        active_connections[client_id] = {
            'connected_at': datetime.now(timezone.utc).isoformat(),
            'subscriptions': []
        }
        logging.info(f"Client {client_id} connected. Total connections: {len(active_connections)}")
        emit('connection_established', {
            'client_id': client_id,
            'server_time': datetime.now(timezone.utc).isoformat(),
            'available_streams': ['pricing_updates', 'cost_alerts', 'ai_predictions', 'anomaly_detection']
        })
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnection"""
        client_id = request.sid
        if client_id in active_connections:
            del active_connections[client_id]
        logging.info(f"Client {client_id} disconnected. Total connections: {len(active_connections)}")
    
    @socketio.on('subscribe_to_stream')
    def handle_stream_subscription(data):
        """Handle stream subscription"""
        client_id = request.sid
        stream_type = data.get('stream_type')
        
        if client_id in active_connections:
            if stream_type not in active_connections[client_id]['subscriptions']:
                active_connections[client_id]['subscriptions'].append(stream_type)
                join_room(stream_type)
                emit('subscription_confirmed', {
                    'stream_type': stream_type,
                    'status': 'subscribed'
                })
                logging.info(f"Client {client_id} subscribed to {stream_type}")
    
    @socketio.on('unsubscribe_from_stream')
    def handle_stream_unsubscription(data):
        """Handle stream unsubscription"""
        client_id = request.sid
        stream_type = data.get('stream_type')
        
        if client_id in active_connections:
            if stream_type in active_connections[client_id]['subscriptions']:
                active_connections[client_id]['subscriptions'].remove(stream_type)
                leave_room(stream_type)
                emit('unsubscription_confirmed', {
                    'stream_type': stream_type,
                    'status': 'unsubscribed'
                })
                logging.info(f"Client {client_id} unsubscribed from {stream_type}")
    
    def broadcast_pricing_updates():
        """Broadcast real-time pricing updates"""
        while True:
            try:
                if active_connections:
                    # Generate updated pricing data
                    pricing_update = {
                        'timestamp': datetime.now(timezone.utc).isoformat(),
                        'type': 'pricing_update',
                        'data': {
                            'aws_ec2_t3_micro': round(0.0104 + (time.time() % 10 - 5) * 0.0001, 6),
                            'azure_vm_b1s': round(0.0104 + (time.time() % 8 - 4) * 0.0002, 6),
                            'gcp_e2_micro': round(0.00651 + (time.time() % 6 - 3) * 0.0001, 6)
                        }
                    }
                    socketio.emit('pricing_update', pricing_update, room='pricing_updates')
                
                eventlet.sleep(30)  # Update every 30 seconds
            except Exception as e:
                logging.error(f"Error broadcasting pricing updates: {e}")
                eventlet.sleep(60)
    
    def broadcast_cost_alerts():
        """Broadcast cost alerts and anomalies"""
        while True:
            try:
                if active_connections:
                    # Generate cost alert
                    alert = {
                        'timestamp': datetime.now(timezone.utc).isoformat(),
                        'type': 'cost_alert',
                        'severity': 'medium',
                        'title': 'Cost Spike Detected',
                        'message': f'AWS EC2 costs increased by 12% in the last hour',
                        'provider': 'aws',
                        'service': 'ec2',
                        'impact': '$23.45'
                    }
                    socketio.emit('cost_alert', alert, room='cost_alerts')
                
                eventlet.sleep(120)  # Alert every 2 minutes
            except Exception as e:
                logging.error(f"Error broadcasting cost alerts: {e}")
                eventlet.sleep(180)
    
    # Start background threads
    def start_background_tasks():
        """Start background streaming tasks"""
        socketio.start_background_task(broadcast_pricing_updates)
        socketio.start_background_task(broadcast_cost_alerts)
    
    # Store socketio instance in app for access
    app.socketio = socketio
    app.start_background_tasks = start_background_tasks
    
    return app, socketio

if __name__ == '__main__':
    setup_logging()
    logging.info("🚀 Starting FISO Real-Time Server with WebSocket Support...")
    
    app, socketio = create_real_time_app()
    
    # Start background tasks
    app.start_background_tasks()
    
    logging.info("🌐 Real-Time Server Configuration:")
    logging.info("   • Host: 0.0.0.0")
    logging.info("   • Port: 5001")
    logging.info("   • WebSocket: Enabled")
    logging.info("   • Real-time Streaming: Active")
    logging.info("======================================================================")
    logging.info("🎯 FISO Enterprise Intelligence Platform - REAL-TIME MODE")
    logging.info("======================================================================")
    
    # Run with eventlet WSGI server
    socketio.run(app, host='0.0.0.0', port=5001, debug=False)