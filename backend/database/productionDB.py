"""
Production Database Service
Replaces SQLite with proper database management and schema
"""

import os
import sqlite3
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json
import threading
from contextlib import contextmanager

class ProductionDatabase:
    """Enhanced database service with proper connection pooling and schema management"""
    
    def __init__(self, db_path: str = "data/fiso_production.db"):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        self._local = threading.local()
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Initialize database
        self.init_database()
        
        # Create indexes for performance
        self.create_indexes()
        
        self.logger.info(f"✅ Production database initialized: {db_path}")
    
    @contextmanager
    def get_connection(self):
        """Get database connection with proper error handling"""
        if not hasattr(self._local, 'connection'):
            self._local.connection = sqlite3.connect(
                self.db_path,
                check_same_thread=False,
                timeout=30.0
            )
            self._local.connection.row_factory = sqlite3.Row
            # Enable WAL mode for better concurrency
            self._local.connection.execute('PRAGMA journal_mode=WAL')
            self._local.connection.execute('PRAGMA synchronous=NORMAL')
            self._local.connection.execute('PRAGMA cache_size=10000')
            self._local.connection.execute('PRAGMA temp_store=MEMORY')
        
        try:
            yield self._local.connection
        except Exception as e:
            self._local.connection.rollback()
            self.logger.error(f"Database error: {str(e)}")
            raise
        finally:
            self._local.connection.commit()
    
    def init_database(self):
        """Initialize database schema"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Cost history table (enhanced)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS cost_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME NOT NULL,
                    provider VARCHAR(255) NOT NULL,
                    service_type VARCHAR(255) NOT NULL,
                    instance_type TEXT,
                    region TEXT DEFAULT 'us-east-1',
                    cost_usd REAL NOT NULL,
                    usage_hours REAL DEFAULT 1.0,
                    usage_quantity REAL DEFAULT 1.0,
                    currency TEXT DEFAULT 'USD',
                    billing_period TEXT DEFAULT 'hourly',
                    metadata TEXT,
                    source TEXT DEFAULT 'api',
                    confidence_score REAL DEFAULT 1.0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Pricing cache table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS pricing_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    provider VARCHAR(255) NOT NULL,
                    service_type VARCHAR(255) NOT NULL,
                    instance_type VARCHAR(255) NOT NULL,
                    region VARCHAR(255) NOT NULL,
                    price_per_hour REAL NOT NULL,
                    currency TEXT DEFAULT 'USD',
                    last_updated DATETIME NOT NULL,
                    expires_at DATETIME NOT NULL,
                    source VARCHAR(255) NOT NULL,
                    confidence_score REAL DEFAULT 1.0,
                    metadata TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(provider, service_type, instance_type, region)
                )
            ''')
            
            # ML model metadata table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ml_models (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    model_key TEXT UNIQUE NOT NULL,
                    model_type VARCHAR(255) NOT NULL,
                    provider VARCHAR(255) NOT NULL,
                    service_type VARCHAR(255) NOT NULL,
                    model_path TEXT,
                    performance_metrics TEXT,
                    training_data_points INTEGER DEFAULT 0,
                    last_trained DATETIME,
                    status TEXT DEFAULT 'active',
                    version TEXT DEFAULT '1.0',
                    metadata TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Anomalies table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS anomalies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME NOT NULL,
                    provider VARCHAR(255) NOT NULL,
                    service_type VARCHAR(255) NOT NULL,
                    anomaly_type VARCHAR(255) NOT NULL,
                    severity VARCHAR(255) NOT NULL,
                    actual_value REAL NOT NULL,
                    expected_value REAL NOT NULL,
                    anomaly_score REAL NOT NULL,
                    description TEXT,
                    status TEXT DEFAULT 'open',
                    detected_by TEXT DEFAULT 'system',
                    metadata TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    resolved_at DATETIME
                )
            ''')
            
            # Optimization recommendations table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS recommendations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    recommendation_id TEXT UNIQUE NOT NULL,
                    category VARCHAR(255) NOT NULL,
                    title VARCHAR(255) NOT NULL,
                    description VARCHAR(255) NOT NULL,
                    provider TEXT,
                    service_type TEXT,
                    potential_savings_usd REAL DEFAULT 0,
                    potential_savings_percent REAL DEFAULT 0,
                    implementation_effort TEXT DEFAULT 'Medium',
                    risk_level TEXT DEFAULT 'Low',
                    priority TEXT DEFAULT 'Medium',
                    confidence_score REAL DEFAULT 0.5,
                    status TEXT DEFAULT 'pending',
                    implementation_steps TEXT,
                    metadata TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    expires_at DATETIME
                )
            ''')
            
            # System metrics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME NOT NULL,
                    metric_type VARCHAR(255) NOT NULL,
                    metric_name VARCHAR(255) NOT NULL,
                    value REAL NOT NULL,
                    unit TEXT,
                    source TEXT DEFAULT 'system',
                    metadata TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # User sessions table (for authentication)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT UNIQUE NOT NULL,
                    user_id VARCHAR(255) NOT NULL,
                    api_key TEXT,
                    permissions TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    expires_at DATETIME NOT NULL,
                    last_activity DATETIME DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'active',
                    metadata TEXT
                )
            ''')
            
            conn.commit()
    
    def create_indexes(self):
        """Create database indexes for performance"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Cost history indexes
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_cost_history_timestamp ON cost_history(timestamp)",
                "CREATE INDEX IF NOT EXISTS idx_cost_history_provider ON cost_history(provider)",
                "CREATE INDEX IF NOT EXISTS idx_cost_history_service ON cost_history(service_type)",
                "CREATE INDEX IF NOT EXISTS idx_cost_history_provider_service ON cost_history(provider, service_type)",
                "CREATE INDEX IF NOT EXISTS idx_cost_history_region ON cost_history(region)",
                
                # Pricing cache indexes
                "CREATE INDEX IF NOT EXISTS idx_pricing_cache_provider ON pricing_cache(provider)",
                "CREATE INDEX IF NOT EXISTS idx_pricing_cache_expires ON pricing_cache(expires_at)",
                "CREATE INDEX IF NOT EXISTS idx_pricing_cache_updated ON pricing_cache(last_updated)",
                
                # Anomalies indexes
                "CREATE INDEX IF NOT EXISTS idx_anomalies_timestamp ON anomalies(timestamp)",
                "CREATE INDEX IF NOT EXISTS idx_anomalies_provider ON anomalies(provider)",
                "CREATE INDEX IF NOT EXISTS idx_anomalies_severity ON anomalies(severity)",
                "CREATE INDEX IF NOT EXISTS idx_anomalies_status ON anomalies(status)",
                
                # Recommendations indexes
                "CREATE INDEX IF NOT EXISTS idx_recommendations_priority ON recommendations(priority)",
                "CREATE INDEX IF NOT EXISTS idx_recommendations_status ON recommendations(status)",
                "CREATE INDEX IF NOT EXISTS idx_recommendations_created ON recommendations(created_at)",
                
                # System metrics indexes
                "CREATE INDEX IF NOT EXISTS idx_system_metrics_timestamp ON system_metrics(timestamp)",
                "CREATE INDEX IF NOT EXISTS idx_system_metrics_type ON system_metrics(metric_type)",
                
                # User sessions indexes
                "CREATE INDEX IF NOT EXISTS idx_user_sessions_expires ON user_sessions(expires_at)",
                "CREATE INDEX IF NOT EXISTS idx_user_sessions_user ON user_sessions(user_id)"
            ]
            
            for index_sql in indexes:
                cursor.execute(index_sql)
            
            conn.commit()
    
    # Cost History Methods
    def insert_cost_record(self, 
                          timestamp: datetime, 
                          provider: str, 
                          service_type: str, 
                          cost_usd: float,
                          instance_type: str = None,
                          region: str = 'us-east-1',
                          metadata: Dict = None) -> int:
        """Insert a cost record"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO cost_history 
                (timestamp, provider, service_type, instance_type, region, cost_usd, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                timestamp.isoformat(),
                provider,
                service_type,
                instance_type,
                region,
                cost_usd,
                json.dumps(metadata) if metadata else None
            ))
            return cursor.lastrowid
    
    def get_cost_history(self, 
                        provider: str = None,
                        service_type: str = None,
                        days_back: int = 30,
                        limit: int = 1000) -> List[Dict[str, Any]]:
        """Get cost history with filtering"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            query = '''
                SELECT * FROM cost_history 
                WHERE timestamp >= datetime('now', '-{} days')
            '''.format(days_back)
            
            params = []
            
            if provider:
                query += " AND provider = ?"
                params.append(provider)
            
            if service_type:
                query += " AND service_type = ?"
                params.append(service_type)
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            return [dict(row) for row in rows]
    
    # Pricing Cache Methods
    def update_pricing_cache(self, 
                           provider: str,
                           service_type: str,
                           instance_type: str,
                           region: str,
                           price_per_hour: float,
                           source: str,
                           expires_in_minutes: int = 60) -> None:
        """Update pricing cache"""
        expires_at = datetime.now() + timedelta(minutes=expires_in_minutes)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO pricing_cache
                (provider, service_type, instance_type, region, price_per_hour, 
                 last_updated, expires_at, source)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                provider, service_type, instance_type, region, price_per_hour,
                datetime.now().isoformat(), expires_at.isoformat(), source
            ))
    
    def get_cached_pricing(self, 
                          provider: str,
                          service_type: str = None,
                          region: str = None) -> List[Dict[str, Any]]:
        """Get cached pricing data"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            query = '''
                SELECT * FROM pricing_cache 
                WHERE provider = ? AND expires_at > datetime('now')
            '''
            params = [provider]
            
            if service_type:
                query += " AND service_type = ?"
                params.append(service_type)
            
            if region:
                query += " AND region = ?"
                params.append(region)
            
            query += " ORDER BY last_updated DESC"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            return [dict(row) for row in rows]
    
    # ML Model Methods
    def save_model_metadata(self, 
                           model_key: str,
                           model_type: str,
                           provider: str,
                           service_type: str,
                           performance_metrics: Dict,
                           training_data_points: int = 0) -> None:
        """Save ML model metadata"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO ml_models
                (model_key, model_type, provider, service_type, performance_metrics,
                 training_data_points, last_trained, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                model_key, model_type, provider, service_type,
                json.dumps(performance_metrics), training_data_points,
                datetime.now().isoformat(), datetime.now().isoformat()
            ))
    
    def get_model_metadata(self, model_key: str = None) -> List[Dict[str, Any]]:
        """Get ML model metadata"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            if model_key:
                cursor.execute("SELECT * FROM ml_models WHERE model_key = ?", (model_key,))
            else:
                cursor.execute("SELECT * FROM ml_models ORDER BY last_trained DESC")
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    # Anomaly Methods
    def insert_anomaly(self, 
                      timestamp: datetime,
                      provider: str,
                      service_type: str,
                      anomaly_type: str,
                      severity: str,
                      actual_value: float,
                      expected_value: float,
                      anomaly_score: float,
                      description: str = None) -> int:
        """Insert anomaly record"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO anomalies
                (timestamp, provider, service_type, anomaly_type, severity,
                 actual_value, expected_value, anomaly_score, description)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                timestamp.isoformat(), provider, service_type, anomaly_type,
                severity, actual_value, expected_value, anomaly_score, description
            ))
            return cursor.lastrowid
    
    def get_anomalies(self, 
                     provider: str = None,
                     severity: str = None,
                     days_back: int = 7,
                     limit: int = 100) -> List[Dict[str, Any]]:
        """Get anomalies with filtering"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            query = '''
                SELECT * FROM anomalies 
                WHERE timestamp >= datetime('now', '-{} days')
            '''.format(days_back)
            
            params = []
            
            if provider:
                query += " AND provider = ?"
                params.append(provider)
            
            if severity:
                query += " AND severity = ?"
                params.append(severity)
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            return [dict(row) for row in rows]
    
    # Recommendation Methods
    def save_recommendation(self, 
                           recommendation_id: str,
                           category: str,
                           title: str,
                           description: str,
                           potential_savings_usd: float = 0,
                           provider: str = None,
                           priority: str = 'Medium',
                           confidence_score: float = 0.5) -> int:
        """Save optimization recommendation"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO recommendations
                (recommendation_id, category, title, description, potential_savings_usd,
                 provider, priority, confidence_score, expires_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                recommendation_id, category, title, description, potential_savings_usd,
                provider, priority, confidence_score,
                (datetime.now() + timedelta(days=30)).isoformat()
            ))
            return cursor.lastrowid
    
    def get_recommendations(self, 
                          provider: str = None,
                          priority: str = None,
                          status: str = 'pending',
                          limit: int = 50) -> List[Dict[str, Any]]:
        """Get optimization recommendations"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            query = "SELECT * FROM recommendations WHERE expires_at > datetime('now')"
            params = []
            
            if provider:
                query += " AND provider = ?"
                params.append(provider)
            
            if priority:
                query += " AND priority = ?"
                params.append(priority)
            
            if status:
                query += " AND status = ?"
                params.append(status)
            
            query += " ORDER BY potential_savings_usd DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            return [dict(row) for row in rows]
    
    # System Metrics Methods
    def record_system_metric(self, 
                            metric_type: str,
                            metric_name: str,
                            value: float,
                            unit: str = None,
                            timestamp: datetime = None) -> int:
        """Record system metric"""
        if timestamp is None:
            timestamp = datetime.now()
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO system_metrics
                (timestamp, metric_type, metric_name, value, unit)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                timestamp.isoformat(), metric_type, metric_name, value, unit
            ))
            return cursor.lastrowid
    
    def get_system_metrics(self, 
                          metric_type: str = None,
                          hours_back: int = 24) -> List[Dict[str, Any]]:
        """Get system metrics"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            query = '''
                SELECT * FROM system_metrics 
                WHERE timestamp >= datetime('now', '-{} hours')
            '''.format(hours_back)
            
            params = []
            
            if metric_type:
                query += " AND metric_type = ?"
                params.append(metric_type)
            
            query += " ORDER BY timestamp DESC"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            return [dict(row) for row in rows]
    
    # Database Maintenance
    def cleanup_old_data(self, days_to_keep: int = 90):
        """Clean up old data to maintain performance"""
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Clean old cost history
            cursor.execute(
                "DELETE FROM cost_history WHERE timestamp < ?",
                (cutoff_date.isoformat(),)
            )
            cost_deleted = cursor.rowcount
            
            # Clean expired pricing cache
            cursor.execute(
                "DELETE FROM pricing_cache WHERE expires_at < datetime('now')"
            )
            cache_deleted = cursor.rowcount
            
            # Clean old system metrics (keep 30 days)
            metrics_cutoff = datetime.now() - timedelta(days=30)
            cursor.execute(
                "DELETE FROM system_metrics WHERE timestamp < ?",
                (metrics_cutoff.isoformat(),)
            )
            metrics_deleted = cursor.rowcount
            
            # Clean resolved anomalies older than 30 days
            cursor.execute(
                "DELETE FROM anomalies WHERE status = 'resolved' AND resolved_at < ?",
                (metrics_cutoff.isoformat(),)
            )
            anomalies_deleted = cursor.rowcount
            
            # Clean expired recommendations
            cursor.execute(
                "DELETE FROM recommendations WHERE expires_at < datetime('now')"
            )
            recommendations_deleted = cursor.rowcount
            
            # Vacuum database
            cursor.execute("VACUUM")
            
            conn.commit()
            
            self.logger.info(f"Database cleanup completed:")
            self.logger.info(f"  - Cost history: {cost_deleted} records")
            self.logger.info(f"  - Pricing cache: {cache_deleted} records")
            self.logger.info(f"  - System metrics: {metrics_deleted} records")
            self.logger.info(f"  - Anomalies: {anomalies_deleted} records")
            self.logger.info(f"  - Recommendations: {recommendations_deleted} records")
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            stats = {}
            
            # Table counts
            tables = ['cost_history', 'pricing_cache', 'ml_models', 'anomalies', 
                     'recommendations', 'system_metrics', 'user_sessions']
            
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                stats[f"{table}_count"] = cursor.fetchone()[0]
            
            # Database size
            cursor.execute("PRAGMA page_count")
            page_count = cursor.fetchone()[0]
            cursor.execute("PRAGMA page_size")
            page_size = cursor.fetchone()[0]
            stats['database_size_mb'] = (page_count * page_size) / (1024 * 1024)
            
            # Recent data
            cursor.execute('''
                SELECT COUNT(*) FROM cost_history 
                WHERE timestamp >= datetime('now', '-24 hours')
            ''')
            stats['recent_cost_records'] = cursor.fetchone()[0]
            
            cursor.execute('''
                SELECT COUNT(*) FROM anomalies 
                WHERE timestamp >= datetime('now', '-24 hours')
            ''')
            stats['recent_anomalies'] = cursor.fetchone()[0]
            
            return stats

# Global database instance
_db_instance = None

def get_database() -> ProductionDatabase:
    """Get or create database instance"""
    global _db_instance
    if _db_instance is None:
        _db_instance = ProductionDatabase()
    return _db_instance

if __name__ == "__main__":
    # Test the database
    db = ProductionDatabase()
    
    # Insert test data
    from datetime import datetime
    import random
    
    print("Testing database...")
    
    # Test cost record
    record_id = db.insert_cost_record(
        timestamp=datetime.now(),
        provider='aws',
        service_type='ec2',
        cost_usd=0.0104,
        instance_type='t3.micro'
    )
    print(f"Inserted cost record: {record_id}")
    
    # Test anomaly
    anomaly_id = db.insert_anomaly(
        timestamp=datetime.now(),
        provider='aws',
        service_type='ec2',
        anomaly_type='cost_spike',
        severity='high',
        actual_value=0.5,
        expected_value=0.01,
        anomaly_score=0.95,
        description='Test anomaly'
    )
    print(f"Inserted anomaly: {anomaly_id}")
    
    # Get stats
    stats = db.get_database_stats()
    print("Database stats:", json.dumps(stats, indent=2))
    
    print("✅ Database test completed")
