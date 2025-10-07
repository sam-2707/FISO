"""
FISO Comprehensive Monitoring Stack
Prometheus metrics, custom dashboards, alerting, and observability
"""

import time
import asyncio
import json
import logging
import structlog
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from prometheus_client import (
    Counter, Histogram, Gauge, Summary, Enum, Info,
    CollectorRegistry, generate_latest, CONTENT_TYPE_LATEST
)
from prometheus_client.multiprocess import MultiProcessCollector
import psutil
import aioredis
import asyncpg
from fastapi import FastAPI, Response, HTTPException
from pydantic import BaseModel
import yaml
import os

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Business Metrics Registry
REGISTRY = CollectorRegistry()

# API Metrics
api_requests_total = Counter(
    'fiso_api_requests_total',
    'Total number of API requests',
    ['method', 'endpoint', 'status_code', 'organization'],
    registry=REGISTRY
)

api_request_duration = Histogram(
    'fiso_api_request_duration_seconds',
    'Time spent processing API requests',
    ['method', 'endpoint', 'organization'],
    registry=REGISTRY
)

api_active_connections = Gauge(
    'fiso_api_active_connections',
    'Number of active API connections',
    registry=REGISTRY
)

# Cost Data Metrics
cost_data_points_total = Counter(
    'fiso_cost_data_points_total',
    'Total number of cost data points processed',
    ['provider', 'service', 'organization'],
    registry=REGISTRY
)

cost_analysis_duration = Histogram(
    'fiso_cost_analysis_duration_seconds',
    'Time spent analyzing cost data',
    ['provider', 'analysis_type'],
    registry=REGISTRY
)

total_cloud_spend = Gauge(
    'fiso_total_cloud_spend_usd',
    'Total cloud spend in USD',
    ['provider', 'organization', 'service'],
    registry=REGISTRY
)

# Optimization Metrics
optimization_recommendations_total = Counter(
    'fiso_optimization_recommendations_total',
    'Total optimization recommendations generated',
    ['provider', 'recommendation_type', 'organization'],
    registry=REGISTRY
)

potential_savings_usd = Gauge(
    'fiso_potential_savings_usd',
    'Potential savings identified in USD',
    ['provider', 'organization', 'recommendation_type'],
    registry=REGISTRY
)

recommendations_implemented = Counter(
    'fiso_recommendations_implemented_total',
    'Number of recommendations implemented',
    ['provider', 'organization', 'recommendation_type'],
    registry=REGISTRY
)

# System Metrics
database_connections = Gauge(
    'fiso_database_connections',
    'Number of active database connections',
    ['database', 'state'],
    registry=REGISTRY
)

cache_hit_rate = Gauge(
    'fiso_cache_hit_rate',
    'Cache hit rate percentage',
    ['cache_type'],
    registry=REGISTRY
)

system_cpu_usage = Gauge(
    'fiso_system_cpu_usage_percent',
    'System CPU usage percentage',
    registry=REGISTRY
)

system_memory_usage = Gauge(
    'fiso_system_memory_usage_bytes',
    'System memory usage in bytes',
    ['type'],  # used, available, total
    registry=REGISTRY
)

# Data Quality Metrics
data_freshness_seconds = Gauge(
    'fiso_data_freshness_seconds',
    'Age of the most recent data in seconds',
    ['provider', 'data_type'],
    registry=REGISTRY
)

data_completeness_ratio = Gauge(
    'fiso_data_completeness_ratio',
    'Ratio of complete data points (0-1)',
    ['provider', 'data_type'],
    registry=REGISTRY
)

# Alert Metrics
alerts_fired_total = Counter(
    'fiso_alerts_fired_total',
    'Total number of alerts fired',
    ['alert_type', 'severity', 'organization'],
    registry=REGISTRY
)

@dataclass
class AlertRule:
    """Alert rule configuration"""
    name: str
    query: str
    threshold: float
    severity: str  # critical, warning, info
    duration: str  # e.g., "5m"
    description: str
    runbook_url: Optional[str] = None
    labels: Dict[str, str] = None

@dataclass
class Dashboard:
    """Grafana dashboard configuration"""
    title: str
    tags: List[str]
    panels: List[Dict[str, Any]]
    refresh: str = "30s"
    time_range: str = "1h"

class MetricsCollector:
    """Collects and exports custom business metrics"""
    
    def __init__(self, redis_url: str, database_url: str):
        self.redis_url = redis_url
        self.database_url = database_url
        self.redis = None
        self.db_pool = None
    
    async def initialize(self):
        """Initialize connections"""
        self.redis = await aioredis.from_url(self.redis_url)
        self.db_pool = await asyncpg.create_pool(self.database_url)
        logger.info("Metrics collector initialized")
    
    async def collect_system_metrics(self):
        """Collect system-level metrics"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            system_cpu_usage.set(cpu_percent)
            
            # Memory usage
            memory = psutil.virtual_memory()
            system_memory_usage.labels(type='used').set(memory.used)
            system_memory_usage.labels(type='available').set(memory.available)
            system_memory_usage.labels(type='total').set(memory.total)
            
            # API connections
            connection_count = len(psutil.net_connections(kind='tcp'))
            api_active_connections.set(connection_count)
            
            logger.debug("System metrics collected", 
                        cpu_percent=cpu_percent, 
                        memory_used_gb=memory.used / (1024**3))
            
        except Exception as e:
            logger.error("Error collecting system metrics", error=str(e))
    
    async def collect_database_metrics(self):
        """Collect database metrics"""
        if not self.db_pool:
            return
        
        try:
            async with self.db_pool.acquire() as conn:
                # Database connections
                result = await conn.fetchrow("""
                    SELECT count(*) as total_connections,
                           count(*) FILTER (WHERE state = 'active') as active_connections,
                           count(*) FILTER (WHERE state = 'idle') as idle_connections
                    FROM pg_stat_activity
                    WHERE datname = current_database()
                """)
                
                database_connections.labels(database='main', state='total').set(result['total_connections'])
                database_connections.labels(database='main', state='active').set(result['active_connections'])
                database_connections.labels(database='main', state='idle').set(result['idle_connections'])
                
                # Data freshness
                freshness_result = await conn.fetchrow("""
                    SELECT 
                        EXTRACT(EPOCH FROM (NOW() - MAX(created_at))) as max_age_seconds
                    FROM cost_data
                    WHERE created_at > NOW() - INTERVAL '24 hours'
                """)
                
                if freshness_result and freshness_result['max_age_seconds']:
                    data_freshness_seconds.labels(provider='all', data_type='cost').set(
                        freshness_result['max_age_seconds']
                    )
                
                logger.debug("Database metrics collected", 
                           total_connections=result['total_connections'],
                           active_connections=result['active_connections'])
                
        except Exception as e:
            logger.error("Error collecting database metrics", error=str(e))
    
    async def collect_cache_metrics(self):
        """Collect cache metrics"""
        if not self.redis:
            return
        
        try:
            # Get Redis info
            info = await self.redis.info()
            
            # Cache hit rate (approximation)
            hits = info.get('keyspace_hits', 0)
            misses = info.get('keyspace_misses', 0)
            total = hits + misses
            
            if total > 0:
                hit_rate = (hits / total) * 100
                cache_hit_rate.labels(cache_type='redis').set(hit_rate)
            
            logger.debug("Cache metrics collected", hit_rate=hit_rate if total > 0 else 0)
            
        except Exception as e:
            logger.error("Error collecting cache metrics", error=str(e))
    
    async def collect_business_metrics(self):
        """Collect business-specific metrics"""
        if not self.db_pool:
            return
        
        try:
            async with self.db_pool.acquire() as conn:
                # Total spend by provider (last 24 hours)
                spend_result = await conn.fetch("""
                    SELECT 
                        cd.provider_id,
                        cp.provider_name,
                        o.name as organization,
                        cd.service_name,
                        SUM(cd.cost_amount) as total_spend
                    FROM cost_data cd
                    JOIN cloud_providers cp ON cd.provider_id = cp.id
                    JOIN organizations o ON cd.organization_id = o.id
                    WHERE cd.usage_date > NOW() - INTERVAL '24 hours'
                    GROUP BY cd.provider_id, cp.provider_name, o.name, cd.service_name
                """)
                
                for row in spend_result:
                    total_cloud_spend.labels(
                        provider=row['provider_name'],
                        organization=row['organization'],
                        service=row['service_name']
                    ).set(row['total_spend'])
                
                # Optimization metrics
                opt_result = await conn.fetch("""
                    SELECT 
                        cp.provider_name,
                        o.name as organization,
                        or.recommendation_type,
                        COUNT(*) as count,
                        SUM(or.estimated_savings) as total_savings
                    FROM optimization_recommendations or
                    JOIN cloud_providers cp ON or.provider_id = cp.id
                    JOIN organizations o ON or.organization_id = o.id
                    WHERE or.status = 'active'
                    GROUP BY cp.provider_name, o.name, or.recommendation_type
                """)
                
                for row in opt_result:
                    potential_savings_usd.labels(
                        provider=row['provider_name'],
                        organization=row['organization'],
                        recommendation_type=row['recommendation_type']
                    ).set(row['total_savings'])
                
                logger.debug("Business metrics collected", 
                           spend_records=len(spend_result),
                           optimization_records=len(opt_result))
                
        except Exception as e:
            logger.error("Error collecting business metrics", error=str(e))
    
    async def collect_all_metrics(self):
        """Collect all metrics"""
        tasks = [
            self.collect_system_metrics(),
            self.collect_database_metrics(),
            self.collect_cache_metrics(),
            self.collect_business_metrics(),
        ]
        
        await asyncio.gather(*tasks, return_exceptions=True)

class AlertManager:
    """Manages alerts and notifications"""
    
    def __init__(self, config_file: str = "config/alerts.yml"):
        self.config_file = config_file
        self.alert_rules = self._load_alert_rules()
        self.notification_channels = self._load_notification_channels()
    
    def _load_alert_rules(self) -> List[AlertRule]:
        """Load alert rules from configuration"""
        try:
            with open(self.config_file, 'r') as f:
                config = yaml.safe_load(f)
            
            rules = []
            for rule_config in config.get('rules', []):
                rule = AlertRule(**rule_config)
                rules.append(rule)
            
            return rules
        except FileNotFoundError:
            logger.warning("Alert configuration file not found, using defaults")
            return self._get_default_alert_rules()
    
    def _get_default_alert_rules(self) -> List[AlertRule]:
        """Get default alert rules"""
        return [
            AlertRule(
                name="HighAPIErrorRate",
                query='rate(fiso_api_requests_total{status_code=~"5.."}[5m]) > 0.1',
                threshold=0.1,
                severity="critical",
                duration="5m",
                description="API error rate is above 10%",
                labels={"team": "platform"}
            ),
            AlertRule(
                name="HighCloudSpend",
                query='increase(fiso_total_cloud_spend_usd[1h]) > 1000',
                threshold=1000,
                severity="warning",
                duration="0m",
                description="Cloud spend increased by $1000+ in the last hour",
                labels={"team": "finops"}
            ),
            AlertRule(
                name="DataFreshnessIssue",
                query='fiso_data_freshness_seconds > 3600',
                threshold=3600,
                severity="warning",
                duration="10m",
                description="Cost data is more than 1 hour old",
                labels={"team": "data"}
            ),
            AlertRule(
                name="DatabaseConnectionsHigh",
                query='fiso_database_connections{state="active"} > 80',
                threshold=80,
                severity="warning",
                duration="5m",
                description="High number of active database connections",
                labels={"team": "platform"}
            )
        ]
    
    def _load_notification_channels(self) -> Dict[str, Dict[str, Any]]:
        """Load notification channels"""
        return {
            "slack": {
                "webhook_url": os.getenv("SLACK_WEBHOOK_URL"),
                "channel": "#fiso-alerts",
                "enabled": bool(os.getenv("SLACK_WEBHOOK_URL"))
            },
            "pagerduty": {
                "integration_key": os.getenv("PAGERDUTY_INTEGRATION_KEY"),
                "enabled": bool(os.getenv("PAGERDUTY_INTEGRATION_KEY"))
            },
            "email": {
                "smtp_host": os.getenv("SMTP_HOST"),
                "smtp_port": int(os.getenv("SMTP_PORT", 587)),
                "username": os.getenv("SMTP_USERNAME"),
                "password": os.getenv("SMTP_PASSWORD"),
                "recipients": os.getenv("ALERT_EMAIL_RECIPIENTS", "").split(","),
                "enabled": bool(os.getenv("SMTP_HOST"))
            }
        }
    
    def generate_prometheus_rules(self) -> str:
        """Generate Prometheus alert rules configuration"""
        rules_config = {
            "groups": [
                {
                    "name": "fiso-alerts",
                    "rules": []
                }
            ]
        }
        
        for rule in self.alert_rules:
            prometheus_rule = {
                "alert": rule.name,
                "expr": rule.query,
                "for": rule.duration,
                "labels": {
                    "severity": rule.severity,
                    **(rule.labels or {})
                },
                "annotations": {
                    "summary": rule.description,
                    "description": rule.description
                }
            }
            
            if rule.runbook_url:
                prometheus_rule["annotations"]["runbook_url"] = rule.runbook_url
            
            rules_config["groups"][0]["rules"].append(prometheus_rule)
        
        return yaml.dump(rules_config, default_flow_style=False)
    
    async def fire_alert(self, alert_name: str, labels: Dict[str, str], annotations: Dict[str, str]):
        """Fire an alert through configured notification channels"""
        try:
            # Record alert metric
            alerts_fired_total.labels(
                alert_type=alert_name,
                severity=labels.get('severity', 'unknown'),
                organization=labels.get('organization', 'unknown')
            ).inc()
            
            # Send notifications
            await self._send_notifications(alert_name, labels, annotations)
            
            logger.warning("Alert fired", 
                         alert=alert_name, 
                         labels=labels, 
                         annotations=annotations)
            
        except Exception as e:
            logger.error("Error firing alert", alert=alert_name, error=str(e))
    
    async def _send_notifications(self, alert_name: str, labels: Dict[str, str], annotations: Dict[str, str]):
        """Send notifications to configured channels"""
        # This would implement actual notification sending
        # For now, just log the notification
        logger.info("Alert notification sent", 
                   alert=alert_name, 
                   channels=list(self.notification_channels.keys()))

class DashboardGenerator:
    """Generates Grafana dashboards"""
    
    def __init__(self):
        self.dashboards = {}
    
    def create_overview_dashboard(self) -> Dashboard:
        """Create main overview dashboard"""
        panels = [
            # API Performance Panel
            {
                "title": "API Request Rate",
                "type": "graph",
                "targets": [
                    {
                        "expr": "rate(fiso_api_requests_total[5m])",
                        "legendFormat": "{{method}} {{endpoint}}"
                    }
                ],
                "yAxes": [{"label": "Requests/sec"}]
            },
            
            # Cost Overview Panel
            {
                "title": "Total Cloud Spend (24h)",
                "type": "stat",
                "targets": [
                    {
                        "expr": "sum(fiso_total_cloud_spend_usd)",
                        "legendFormat": "Total Spend"
                    }
                ],
                "unit": "currencyUSD"
            },
            
            # Optimization Savings Panel
            {
                "title": "Potential Savings",
                "type": "piechart",
                "targets": [
                    {
                        "expr": "sum by (provider) (fiso_potential_savings_usd)",
                        "legendFormat": "{{provider}}"
                    }
                ]
            },
            
            # System Health Panel
            {
                "title": "System Resources",
                "type": "graph",
                "targets": [
                    {
                        "expr": "fiso_system_cpu_usage_percent",
                        "legendFormat": "CPU %"
                    },
                    {
                        "expr": "fiso_system_memory_usage_bytes{type='used'} / fiso_system_memory_usage_bytes{type='total'} * 100",
                        "legendFormat": "Memory %"
                    }
                ]
            }
        ]
        
        return Dashboard(
            title="FISO - Overview",
            tags=["fiso", "overview"],
            panels=panels
        )
    
    def create_cost_analysis_dashboard(self) -> Dashboard:
        """Create cost analysis dashboard"""
        panels = [
            {
                "title": "Cost by Provider",
                "type": "graph",
                "targets": [
                    {
                        "expr": "sum by (provider) (fiso_total_cloud_spend_usd)",
                        "legendFormat": "{{provider}}"
                    }
                ]
            },
            {
                "title": "Cost by Service",
                "type": "table",
                "targets": [
                    {
                        "expr": "topk(10, sum by (service) (fiso_total_cloud_spend_usd))",
                        "format": "table"
                    }
                ]
            },
            {
                "title": "Cost Trend (7 days)",
                "type": "graph",
                "targets": [
                    {
                        "expr": "sum(fiso_total_cloud_spend_usd)",
                        "legendFormat": "Daily Spend"
                    }
                ]
            }
        ]
        
        return Dashboard(
            title="FISO - Cost Analysis",
            tags=["fiso", "cost", "analysis"],
            panels=panels
        )
    
    def generate_json_dashboard(self, dashboard: Dashboard) -> Dict[str, Any]:
        """Generate Grafana JSON dashboard"""
        return {
            "dashboard": {
                "title": dashboard.title,
                "tags": dashboard.tags,
                "time": {
                    "from": f"now-{dashboard.time_range}",
                    "to": "now"
                },
                "refresh": dashboard.refresh,
                "panels": dashboard.panels,
                "version": 1
            },
            "overwrite": True
        }

class MonitoringService:
    """Main monitoring service orchestrator"""
    
    def __init__(self, config_file: str = "config/monitoring.yml"):
        self.config = self._load_config(config_file)
        self.metrics_collector = None
        self.alert_manager = None
        self.dashboard_generator = None
    
    def _load_config(self, config_file: str) -> Dict[str, Any]:
        """Load monitoring configuration"""
        try:
            with open(config_file, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.warning("Monitoring configuration file not found, using defaults")
            return {
                "collection": {
                    "interval_seconds": 30,
                    "enabled": True
                },
                "alerts": {
                    "enabled": True,
                    "evaluation_interval": "30s"
                },
                "dashboards": {
                    "auto_create": True
                }
            }
    
    async def initialize(self):
        """Initialize monitoring service"""
        logger.info("Initializing monitoring service")
        
        # Initialize metrics collector
        self.metrics_collector = MetricsCollector(
            redis_url=os.getenv("REDIS_URL", "redis://localhost:6379"),
            database_url=os.getenv("DATABASE_URL", "postgresql://user:password@localhost/fiso_db")
        )
        await self.metrics_collector.initialize()
        
        # Initialize alert manager
        self.alert_manager = AlertManager()
        
        # Initialize dashboard generator
        self.dashboard_generator = DashboardGenerator()
        
        logger.info("Monitoring service initialized successfully")
    
    async def start_collection_loop(self):
        """Start the metrics collection loop"""
        interval = self.config['collection']['interval_seconds']
        
        logger.info("Starting metrics collection loop", interval_seconds=interval)
        
        while True:
            try:
                await self.metrics_collector.collect_all_metrics()
                logger.debug("Metrics collection completed")
                
            except Exception as e:
                logger.error("Error in metrics collection loop", error=str(e))
            
            await asyncio.sleep(interval)
    
    def get_prometheus_metrics(self) -> str:
        """Get Prometheus metrics"""
        return generate_latest(REGISTRY)
    
    def get_alert_rules(self) -> str:
        """Get Prometheus alert rules configuration"""
        return self.alert_manager.generate_prometheus_rules()
    
    def get_dashboards(self) -> Dict[str, Dict[str, Any]]:
        """Get Grafana dashboards"""
        overview = self.dashboard_generator.create_overview_dashboard()
        cost_analysis = self.dashboard_generator.create_cost_analysis_dashboard()
        
        return {
            "overview": self.dashboard_generator.generate_json_dashboard(overview),
            "cost_analysis": self.dashboard_generator.generate_json_dashboard(cost_analysis)
        }

# FastAPI app for metrics endpoint
monitoring_app = FastAPI(title="FISO Monitoring", version="1.0.0")

@monitoring_app.on_event("startup")
async def startup_event():
    monitoring_app.state.monitoring_service = MonitoringService()
    await monitoring_app.state.monitoring_service.initialize()
    
    # Start metrics collection in background
    asyncio.create_task(monitoring_app.state.monitoring_service.start_collection_loop())

@monitoring_app.get("/metrics")
async def get_metrics():
    """Prometheus metrics endpoint"""
    metrics = monitoring_app.state.monitoring_service.get_prometheus_metrics()
    return Response(content=metrics, media_type=CONTENT_TYPE_LATEST)

@monitoring_app.get("/alerts")
async def get_alert_rules():
    """Get Prometheus alert rules"""
    rules = monitoring_app.state.monitoring_service.get_alert_rules()
    return Response(content=rules, media_type="text/yaml")

@monitoring_app.get("/dashboards")
async def get_dashboards():
    """Get Grafana dashboards"""
    return monitoring_app.state.monitoring_service.get_dashboards()

@monitoring_app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "monitoring"
    }

# Create configuration templates
def create_monitoring_config_templates():
    """Create monitoring configuration templates"""
    os.makedirs("config", exist_ok=True)
    
    # Monitoring configuration
    monitoring_config = {
        "collection": {
            "interval_seconds": 30,
            "enabled": True
        },
        "alerts": {
            "enabled": True,
            "evaluation_interval": "30s"
        },
        "dashboards": {
            "auto_create": True
        }
    }
    
    with open("config/monitoring.yml", "w") as f:
        yaml.dump(monitoring_config, f, default_flow_style=False)
    
    # Alert configuration
    alert_config = {
        "rules": [
            {
                "name": "HighAPIErrorRate",
                "query": 'rate(fiso_api_requests_total{status_code=~"5.."}[5m]) > 0.1',
                "threshold": 0.1,
                "severity": "critical",
                "duration": "5m",
                "description": "API error rate is above 10%",
                "labels": {"team": "platform"}
            }
        ]
    }
    
    with open("config/alerts.yml", "w") as f:
        yaml.dump(alert_config, f, default_flow_style=False)
    
    logger.info("Created monitoring configuration templates")

if __name__ == "__main__":
    import uvicorn
    
    # Create configuration templates
    create_monitoring_config_templates()
    
    # Run monitoring service
    uvicorn.run(
        "monitoring_stack:monitoring_app",
        host="0.0.0.0",
        port=9090,
        reload=True
    )