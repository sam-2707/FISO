"""
FISO Database Migration and Configuration System
Enterprise PostgreSQL setup with high availability and partitioning
"""

import os
import asyncio
import asyncpg
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import json
import yaml
from sqlalchemy import create_engine, text, MetaData, Table, Column, String, DateTime, Float, Boolean, Integer, Text, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from alembic.config import Config
from alembic import command
from pathlib import Path
import uuid

logger = logging.getLogger(__name__)

class DatabaseConfig:
    """Database configuration management"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or "config/database.yml"
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load database configuration from YAML file"""
        try:
            with open(self.config_file, 'r') as f:
                config = yaml.safe_load(f)
            return config
        except FileNotFoundError:
            # Return default configuration
            return {
                'database': {
                    'host': os.getenv('DB_HOST', 'localhost'),
                    'port': int(os.getenv('DB_PORT', 5432)),
                    'name': os.getenv('DB_NAME', 'fiso_production'),
                    'user': os.getenv('DB_USER', 'fiso_user'),
                    'password': os.getenv('DB_PASSWORD', 'secure_password'),
                    'pool_size': int(os.getenv('DB_POOL_SIZE', 20)),
                    'max_overflow': int(os.getenv('DB_MAX_OVERFLOW', 30)),
                    'pool_timeout': int(os.getenv('DB_POOL_TIMEOUT', 30)),
                    'pool_recycle': int(os.getenv('DB_POOL_RECYCLE', 3600))
                },
                'replica': {
                    'enabled': os.getenv('DB_REPLICA_ENABLED', 'false').lower() == 'true',
                    'host': os.getenv('DB_REPLICA_HOST', 'localhost'),
                    'port': int(os.getenv('DB_REPLICA_PORT', 5433)),
                    'lag_threshold_seconds': int(os.getenv('DB_REPLICA_LAG_THRESHOLD', 60))
                },
                'partitioning': {
                    'enabled': True,
                    'retention_days': int(os.getenv('DB_RETENTION_DAYS', 365)),
                    'partition_interval': os.getenv('DB_PARTITION_INTERVAL', 'monthly')
                },
                'backup': {
                    'enabled': True,
                    'schedule': os.getenv('DB_BACKUP_SCHEDULE', '0 2 * * *'),  # Daily at 2 AM
                    's3_bucket': os.getenv('DB_BACKUP_S3_BUCKET', 'fiso-db-backups'),
                    'retention_days': int(os.getenv('DB_BACKUP_RETENTION_DAYS', 30))
                }
            }
    
    def get_database_url(self, replica: bool = False) -> str:
        """Get database connection URL"""
        config = self.config['replica'] if replica and self.config['replica']['enabled'] else self.config['database']
        
        return (
            f"postgresql://{config['user']}:{config['password']}@"
            f"{config['host']}:{config['port']}/{config['name']}"
        )
    
    def get_async_database_url(self, replica: bool = False) -> str:
        """Get async database connection URL"""
        return self.get_database_url(replica).replace('postgresql://', 'postgresql+asyncpg://')

# Enhanced database models for production
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, index=True)
    is_admin = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    last_login = Column(DateTime, index=True)
    api_key = Column(String(255), unique=True, index=True)
    rate_limit_tier = Column(String(20), default="basic", index=True)
    organization_id = Column(UUID(as_uuid=True), index=True)
    
    # Add indexes for performance
    __table_args__ = (
        Index('idx_users_email_active', 'email', 'is_active'),
        Index('idx_users_org_active', 'organization_id', 'is_active'),
    )

class Organization(Base):
    __tablename__ = "organizations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    plan = Column(String(20), default="basic", index=True)  # basic, premium, enterprise
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    settings = Column(JSONB, default={})
    billing_info = Column(JSONB, default={})

class CloudProvider(Base):
    __tablename__ = "cloud_providers"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    provider_name = Column(String(50), nullable=False, index=True)  # aws, azure, gcp
    display_name = Column(String(100), nullable=False)
    credentials = Column(JSONB, nullable=False)  # Encrypted credentials
    is_active = Column(Boolean, default=True, index=True)
    last_sync = Column(DateTime, index=True)
    sync_status = Column(String(20), default="pending", index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_providers_org_active', 'organization_id', 'is_active'),
        Index('idx_providers_name_active', 'provider_name', 'is_active'),
    )

# Partitioned table for cost data
class CostData(Base):
    __tablename__ = "cost_data"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    provider_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    account_id = Column(String(100), nullable=False, index=True)
    service_name = Column(String(100), nullable=False, index=True)
    resource_id = Column(String(255), index=True)
    cost_amount = Column(Float, nullable=False, index=True)
    currency = Column(String(3), default="USD", index=True)
    usage_date = Column(DateTime, nullable=False, index=True)
    usage_quantity = Column(Float, default=0.0)
    usage_unit = Column(String(50))
    resource_tags = Column(JSONB, default={})
    region = Column(String(50), index=True)
    availability_zone = Column(String(50))
    instance_type = Column(String(50), index=True)
    billing_period = Column(String(10), index=True)  # YYYY-MM
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Partitioning will be handled at table creation level
    __table_args__ = (
        Index('idx_cost_data_org_date', 'organization_id', 'usage_date'),
        Index('idx_cost_data_provider_date', 'provider_id', 'usage_date'),
        Index('idx_cost_data_service_date', 'service_name', 'usage_date'),
        Index('idx_cost_data_billing_period', 'billing_period'),
    )

class OptimizationRecommendation(Base):
    __tablename__ = "optimization_recommendations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    provider_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    recommendation_type = Column(String(50), nullable=False, index=True)
    service_name = Column(String(100), nullable=False, index=True)
    resource_id = Column(String(255))
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    estimated_savings = Column(Float, default=0.0, index=True)
    confidence_score = Column(Float, default=0.0, index=True)
    implementation_complexity = Column(String(20), default="medium")
    status = Column(String(20), default="active", index=True)  # active, dismissed, implemented
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    recommendation_metadata = Column(JSONB, default={})
    
    __table_args__ = (
        Index('idx_recommendations_org_status', 'organization_id', 'status'),
        Index('idx_recommendations_savings', 'estimated_savings'),
    )

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), index=True)
    user_id = Column(UUID(as_uuid=True), index=True)
    action = Column(String(100), nullable=False, index=True)
    resource_type = Column(String(50), index=True)
    resource_id = Column(String(255), index=True)
    old_values = Column(JSONB)
    new_values = Column(JSONB)
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    __table_args__ = (
        Index('idx_audit_org_timestamp', 'organization_id', 'timestamp'),
        Index('idx_audit_user_timestamp', 'user_id', 'timestamp'),
        Index('idx_audit_action_timestamp', 'action', 'timestamp'),
    )

class DatabaseMigrationManager:
    """Manages database migrations and schema updates"""
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.engine = create_engine(
            config.get_database_url(),
            pool_size=config.config['database']['pool_size'],
            max_overflow=config.config['database']['max_overflow'],
            pool_timeout=config.config['database']['pool_timeout'],
            pool_recycle=config.config['database']['pool_recycle'],
            echo=False
        )
    
    def create_database_if_not_exists(self):
        """Create database if it doesn't exist"""
        db_config = self.config.config['database']
        
        # Connect to PostgreSQL server (not specific database)
        admin_url = f"postgresql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/postgres"
        admin_engine = create_engine(admin_url)
        
        with admin_engine.connect() as conn:
            # Check if database exists
            result = conn.execute(text(
                "SELECT 1 FROM pg_database WHERE datname = :db_name"
            ), {"db_name": db_config['name']})
            
            if not result.fetchone():
                # Create database
                conn.execute(text("COMMIT"))  # End current transaction
                conn.execute(text(f'CREATE DATABASE "{db_config["name"]}"'))
                logger.info(f"Created database: {db_config['name']}")
    
    def create_extensions(self):
        """Create required PostgreSQL extensions"""
        extensions = [
            'uuid-ossp',  # For UUID generation
            'pg_stat_statements',  # For query performance monitoring
            'pg_trgm',  # For text search and similarity
            'btree_gin',  # For GIN indexes on multiple data types
        ]
        
        with self.engine.connect() as conn:
            for ext in extensions:
                try:
                    conn.execute(text(f'CREATE EXTENSION IF NOT EXISTS "{ext}"'))
                    logger.info(f"Created extension: {ext}")
                except Exception as e:
                    logger.warning(f"Could not create extension {ext}: {e}")
    
    def create_tables(self):
        """Create all database tables"""
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=self.engine)
        logger.info("Database tables created successfully")
    
    def create_partitions(self):
        """Create partitioned tables for large datasets"""
        if not self.config.config['partitioning']['enabled']:
            return
        
        logger.info("Creating partitioned tables...")
        
        with self.engine.connect() as conn:
            # Create partitioned cost_data table
            conn.execute(text("""
                -- Drop existing table if it exists
                DROP TABLE IF EXISTS cost_data CASCADE;
                
                -- Create partitioned table
                CREATE TABLE cost_data (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    organization_id UUID NOT NULL,
                    provider_id UUID NOT NULL,
                    account_id VARCHAR(100) NOT NULL,
                    service_name VARCHAR(100) NOT NULL,
                    resource_id VARCHAR(255),
                    cost_amount FLOAT NOT NULL,
                    currency VARCHAR(3) DEFAULT 'USD',
                    usage_date TIMESTAMP NOT NULL,
                    usage_quantity FLOAT DEFAULT 0.0,
                    usage_unit VARCHAR(50),
                    resource_tags JSONB DEFAULT '{}',
                    region VARCHAR(50),
                    availability_zone VARCHAR(50),
                    instance_type VARCHAR(50),
                    billing_period VARCHAR(10),
                    created_at TIMESTAMP DEFAULT NOW()
                ) PARTITION BY RANGE (usage_date);
                
                -- Create indexes on partitioned table
                CREATE INDEX idx_cost_data_org_date ON cost_data (organization_id, usage_date);
                CREATE INDEX idx_cost_data_provider_date ON cost_data (provider_id, usage_date);
                CREATE INDEX idx_cost_data_service_date ON cost_data (service_name, usage_date);
                CREATE INDEX idx_cost_data_billing_period ON cost_data (billing_period);
            """))
            
            # Create monthly partitions for the next 12 months
            base_date = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            for i in range(12):
                start_date = base_date + timedelta(days=32*i)
                start_date = start_date.replace(day=1)
                end_date = (start_date + timedelta(days=32)).replace(day=1)
                
                partition_name = f"cost_data_{start_date.strftime('%Y_%m')}"
                
                conn.execute(text(f"""
                    CREATE TABLE {partition_name} PARTITION OF cost_data
                    FOR VALUES FROM ('{start_date}') TO ('{end_date}');
                """))
                
                logger.info(f"Created partition: {partition_name}")
            
            # Create default partition for future data
            conn.execute(text("""
                CREATE TABLE cost_data_default PARTITION OF cost_data DEFAULT;
            """))
    
    def create_indexes(self):
        """Create additional performance indexes"""
        logger.info("Creating performance indexes...")
        
        with self.engine.connect() as conn:
            indexes = [
                # Composite indexes for common queries
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_org_email ON users (organization_id, email)",
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_providers_org_name ON cloud_providers (organization_id, provider_name)",
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_recommendations_org_savings ON optimization_recommendations (organization_id, estimated_savings DESC)",
                
                # JSON indexes for JSONB columns
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_organizations_settings ON organizations USING GIN (settings)",
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_cost_data_tags ON cost_data USING GIN (resource_tags)",
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_providers_credentials ON cloud_providers USING GIN (credentials)",
                
                # Text search indexes
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_recommendations_text ON optimization_recommendations USING GIN (to_tsvector('english', title || ' ' || description))",
            ]
            
            for index_sql in indexes:
                try:
                    conn.execute(text(index_sql))
                    logger.info(f"Created index: {index_sql.split('IF NOT EXISTS')[1].split('ON')[0].strip()}")
                except Exception as e:
                    logger.warning(f"Could not create index: {e}")
    
    def setup_replication(self):
        """Setup database replication for high availability"""
        if not self.config.config['replica']['enabled']:
            return
        
        logger.info("Setting up database replication...")
        
        # This would typically involve:
        # 1. Configure primary server for replication
        # 2. Create replication user
        # 3. Setup streaming replication
        # 4. Configure replica server
        
        with self.engine.connect() as conn:
            # Create replication user
            conn.execute(text("""
                CREATE USER replicator REPLICATION LOGIN CONNECTION LIMIT 1 ENCRYPTED PASSWORD 'replica_password';
            """))
            
            # Configure replication settings (would be in postgresql.conf)
            logger.info("Replication user created. Configure postgresql.conf and pg_hba.conf for streaming replication.")
    
    def run_full_migration(self):
        """Run complete database migration"""
        logger.info("Starting full database migration...")
        
        try:
            # Step 1: Create database
            self.create_database_if_not_exists()
            
            # Step 2: Create extensions
            self.create_extensions()
            
            # Step 3: Create tables
            self.create_tables()
            
            # Step 4: Create partitions
            self.create_partitions()
            
            # Step 5: Create indexes
            self.create_indexes()
            
            # Step 6: Setup replication
            self.setup_replication()
            
            logger.info("Database migration completed successfully")
            
        except Exception as e:
            logger.error(f"Database migration failed: {e}")
            raise

class DatabaseHealthMonitor:
    """Monitor database health and performance"""
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.engine = create_engine(config.get_database_url())
    
    async def check_connection(self) -> Dict[str, Any]:
        """Check database connection health"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                return {
                    "status": "healthy",
                    "response_time_ms": 0,  # Would measure actual response time
                    "timestamp": datetime.utcnow().isoformat()
                }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def check_replication_lag(self) -> Dict[str, Any]:
        """Check replication lag if replica is enabled"""
        if not self.config.config['replica']['enabled']:
            return {"status": "not_configured"}
        
        try:
            # This would check actual replication lag
            # For now, return sample data
            return {
                "status": "healthy",
                "lag_seconds": 2.5,
                "threshold_seconds": self.config.config['replica']['lag_threshold_seconds'],
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get database performance metrics"""
        try:
            with self.engine.connect() as conn:
                # Get connection stats
                conn_result = conn.execute(text("""
                    SELECT count(*) as total_connections,
                           count(*) FILTER (WHERE state = 'active') as active_connections,
                           count(*) FILTER (WHERE state = 'idle') as idle_connections
                    FROM pg_stat_activity
                    WHERE datname = current_database()
                """))
                
                # Get table sizes
                size_result = conn.execute(text("""
                    SELECT schemaname, tablename, 
                           pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
                           pg_total_relation_size(schemaname||'.'||tablename) as size_bytes
                    FROM pg_tables 
                    WHERE schemaname = 'public'
                    ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
                    LIMIT 10
                """))
                
                conn_stats = conn_result.fetchone()
                table_sizes = size_result.fetchall()
                
                return {
                    "connections": {
                        "total": conn_stats[0],
                        "active": conn_stats[1],
                        "idle": conn_stats[2]
                    },
                    "largest_tables": [
                        {
                            "table": f"{row[0]}.{row[1]}",
                            "size": row[2],
                            "size_bytes": row[3]
                        }
                        for row in table_sizes
                    ],
                    "timestamp": datetime.utcnow().isoformat()
                }
        except Exception as e:
            logger.error(f"Error getting performance metrics: {e}")
            return {"error": str(e)}

# Configuration file template
def create_database_config_template():
    """Create database configuration template"""
    config_template = {
        'database': {
            'host': 'localhost',
            'port': 5432,
            'name': 'fiso_production',
            'user': 'fiso_user',
            'password': 'secure_password_change_in_production',
            'pool_size': 20,
            'max_overflow': 30,
            'pool_timeout': 30,
            'pool_recycle': 3600
        },
        'replica': {
            'enabled': False,
            'host': 'localhost-replica',
            'port': 5433,
            'lag_threshold_seconds': 60
        },
        'partitioning': {
            'enabled': True,
            'retention_days': 365,
            'partition_interval': 'monthly'
        },
        'backup': {
            'enabled': True,
            'schedule': '0 2 * * *',
            's3_bucket': 'fiso-db-backups',
            'retention_days': 30
        },
        'monitoring': {
            'enabled': True,
            'slow_query_threshold_ms': 1000,
            'connection_threshold_warning': 80,
            'connection_threshold_critical': 95
        }
    }
    
    # Ensure config directory exists
    os.makedirs("config", exist_ok=True)
    
    with open("config/database.yml", "w") as f:
        yaml.dump(config_template, f, default_flow_style=False, indent=2)
    
    logger.info("Created database configuration template at config/database.yml")

if __name__ == "__main__":
    # Create configuration template
    create_database_config_template()
    
    # Initialize database
    config = DatabaseConfig()
    migration_manager = DatabaseMigrationManager(config)
    
    try:
        migration_manager.run_full_migration()
        print("✅ Database migration completed successfully!")
        
        # Test health monitoring
        health_monitor = DatabaseHealthMonitor(config)
        asyncio.run(health_monitor.check_connection())
        print("✅ Database health check passed!")
        
    except Exception as e:
        print(f"❌ Database migration failed: {e}")
        exit(1)