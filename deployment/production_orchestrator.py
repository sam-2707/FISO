"""
FISO Production Deployment Orchestration
Docker Compose, Kubernetes, and infrastructure management
"""

import os
import yaml
import json
import subprocess
import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class DeploymentConfig:
    """Deployment configuration"""
    environment: str  # development, staging, production
    replicas: int
    resources: Dict[str, str]
    secrets: Dict[str, str]
    config_maps: Dict[str, Any]

class DockerComposeGenerator:
    """Generates Docker Compose configurations"""
    
    def __init__(self, environment: str = "production"):
        self.environment = environment
    
    def generate_production_compose(self) -> Dict[str, Any]:
        """Generate production Docker Compose configuration"""
        return {
            "version": "3.8",
            "services": {
                # Load Balancer (Nginx)
                "nginx": {
                    "image": "nginx:alpine",
                    "ports": ["80:80", "443:443"],
                    "volumes": [
                        "./nginx/nginx.conf:/etc/nginx/nginx.conf:ro",
                        "./nginx/ssl:/etc/nginx/ssl:ro",
                        "./nginx/logs:/var/log/nginx"
                    ],
                    "depends_on": ["api", "frontend"],
                    "restart": "unless-stopped",
                    "networks": ["fiso-network"]
                },
                
                # FISO API Service
                "api": {
                    "build": {
                        "context": ".",
                        "dockerfile": "api/Dockerfile.production"
                    },
                    "environment": [
                        "DATABASE_URL=${DATABASE_URL}",
                        "REDIS_URL=${REDIS_URL}",
                        "SECRET_KEY=${SECRET_KEY}",
                        "AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}",
                        "AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}",
                        "AZURE_TENANT_ID=${AZURE_TENANT_ID}",
                        "AZURE_CLIENT_ID=${AZURE_CLIENT_ID}",
                        "AZURE_CLIENT_SECRET=${AZURE_CLIENT_SECRET}",
                        "GCP_PROJECT_ID=${GCP_PROJECT_ID}",
                        "PROMETHEUS_MULTIPROC_DIR=/tmp/prometheus_multiproc"
                    ],
                    "volumes": [
                        "./logs:/app/logs",
                        "/tmp/prometheus_multiproc:/tmp/prometheus_multiproc"
                    ],
                    "depends_on": ["postgres", "redis"],
                    "restart": "unless-stopped",
                    "networks": ["fiso-network"],
                    "deploy": {
                        "replicas": 3,
                        "resources": {
                            "limits": {
                                "memory": "2G",
                                "cpus": "1.0"
                            },
                            "reservations": {
                                "memory": "1G",
                                "cpus": "0.5"
                            }
                        }
                    },
                    "healthcheck": {
                        "test": ["CMD", "curl", "-f", "http://localhost:8000/health"],
                        "interval": "30s",
                        "timeout": "10s",
                        "retries": 3,
                        "start_period": "60s"
                    }
                },
                
                # Frontend Service
                "frontend": {
                    "build": {
                        "context": "./frontend",
                        "dockerfile": "Dockerfile.production"
                    },
                    "environment": [
                        "REACT_APP_API_URL=${REACT_APP_API_URL}",
                        "REACT_APP_ENVIRONMENT=production"
                    ],
                    "restart": "unless-stopped",
                    "networks": ["fiso-network"],
                    "deploy": {
                        "replicas": 2,
                        "resources": {
                            "limits": {
                                "memory": "512M",
                                "cpus": "0.5"
                            }
                        }
                    }
                },
                
                # PostgreSQL Database
                "postgres": {
                    "image": "postgres:15-alpine",
                    "environment": [
                        "POSTGRES_DB=${POSTGRES_DB}",
                        "POSTGRES_USER=${POSTGRES_USER}",
                        "POSTGRES_PASSWORD=${POSTGRES_PASSWORD}",
                        "POSTGRES_INITDB_ARGS=--auth-host=scram-sha-256"
                    ],
                    "volumes": [
                        "postgres_data:/var/lib/postgresql/data",
                        "./database/init:/docker-entrypoint-initdb.d",
                        "./database/postgresql.conf:/etc/postgresql/postgresql.conf",
                        "./logs/postgres:/var/log/postgresql"
                    ],
                    "ports": ["5432:5432"],
                    "restart": "unless-stopped",
                    "networks": ["fiso-network"],
                    "command": [
                        "postgres",
                        "-c", "config_file=/etc/postgresql/postgresql.conf",
                        "-c", "log_destination=stderr,csvlog",
                        "-c", "logging_collector=on",
                        "-c", "log_directory=/var/log/postgresql",
                        "-c", "log_filename=postgresql-%Y-%m-%d.log"
                    ],
                    "healthcheck": {
                        "test": ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"],
                        "interval": "30s",
                        "timeout": "10s",
                        "retries": 5
                    }
                },
                
                # Redis Cache
                "redis": {
                    "image": "redis:7-alpine",
                    "command": [
                        "redis-server",
                        "--appendonly", "yes",
                        "--maxmemory", "1gb",
                        "--maxmemory-policy", "allkeys-lru"
                    ],
                    "volumes": [
                        "redis_data:/data",
                        "./logs/redis:/var/log/redis"
                    ],
                    "ports": ["6379:6379"],
                    "restart": "unless-stopped",
                    "networks": ["fiso-network"],
                    "healthcheck": {
                        "test": ["CMD", "redis-cli", "ping"],
                        "interval": "30s",
                        "timeout": "10s",
                        "retries": 3
                    }
                },
                
                # Prometheus Monitoring
                "prometheus": {
                    "image": "prom/prometheus:latest",
                    "ports": ["9090:9090"],
                    "volumes": [
                        "./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml:ro",
                        "./monitoring/alerts.yml:/etc/prometheus/alerts.yml:ro",
                        "prometheus_data:/prometheus"
                    ],
                    "command": [
                        "--config.file=/etc/prometheus/prometheus.yml",
                        "--storage.tsdb.path=/prometheus",
                        "--web.console.libraries=/etc/prometheus/console_libraries",
                        "--web.console.templates=/etc/prometheus/consoles",
                        "--storage.tsdb.retention.time=30d",
                        "--web.enable-lifecycle",
                        "--web.enable-admin-api"
                    ],
                    "restart": "unless-stopped",
                    "networks": ["fiso-network"]
                },
                
                # Grafana Dashboards
                "grafana": {
                    "image": "grafana/grafana:latest",
                    "ports": ["3000:3000"],
                    "environment": [
                        "GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_ADMIN_PASSWORD}",
                        "GF_USERS_ALLOW_SIGN_UP=false",
                        "GF_INSTALL_PLUGINS=grafana-piechart-panel"
                    ],
                    "volumes": [
                        "grafana_data:/var/lib/grafana",
                        "./monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards:ro",
                        "./monitoring/grafana/datasources:/etc/grafana/provisioning/datasources:ro"
                    ],
                    "restart": "unless-stopped",
                    "networks": ["fiso-network"],
                    "depends_on": ["prometheus"]
                },
                
                # Log Aggregation (ELK Stack)
                "elasticsearch": {
                    "image": "docker.elastic.co/elasticsearch/elasticsearch:8.8.0",
                    "environment": [
                        "discovery.type=single-node",
                        "ES_JAVA_OPTS=-Xms1g -Xmx1g",
                        "xpack.security.enabled=false"
                    ],
                    "ports": ["9200:9200"],
                    "volumes": ["elasticsearch_data:/usr/share/elasticsearch/data"],
                    "restart": "unless-stopped",
                    "networks": ["fiso-network"]
                },
                
                "logstash": {
                    "image": "docker.elastic.co/logstash/logstash:8.8.0",
                    "volumes": [
                        "./monitoring/logstash/pipeline:/usr/share/logstash/pipeline:ro",
                        "./logs:/logs:ro"
                    ],
                    "depends_on": ["elasticsearch"],
                    "restart": "unless-stopped",
                    "networks": ["fiso-network"]
                },
                
                "kibana": {
                    "image": "docker.elastic.co/kibana/kibana:8.8.0",
                    "ports": ["5601:5601"],
                    "environment": [
                        "ELASTICSEARCH_HOSTS=http://elasticsearch:9200"
                    ],
                    "depends_on": ["elasticsearch"],
                    "restart": "unless-stopped",
                    "networks": ["fiso-network"]
                }
            },
            
            "networks": {
                "fiso-network": {
                    "driver": "bridge"
                }
            },
            
            "volumes": {
                "postgres_data": {},
                "redis_data": {},
                "prometheus_data": {},
                "grafana_data": {},
                "elasticsearch_data": {}
            }
        }
    
    def save_compose_file(self, config: Dict[str, Any], filename: str = "docker-compose.production.yml"):
        """Save Docker Compose configuration to file"""
        with open(filename, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, indent=2)
        logger.info(f"Docker Compose configuration saved to {filename}")

class KubernetesManifestGenerator:
    """Generates Kubernetes deployment manifests"""
    
    def __init__(self, namespace: str = "fiso-production"):
        self.namespace = namespace
    
    def generate_namespace(self) -> Dict[str, Any]:
        """Generate namespace manifest"""
        return {
            "apiVersion": "v1",
            "kind": "Namespace",
            "metadata": {
                "name": self.namespace,
                "labels": {
                    "app": "fiso",
                    "environment": "production"
                }
            }
        }
    
    def generate_api_deployment(self, config: DeploymentConfig) -> Dict[str, Any]:
        """Generate API deployment manifest"""
        return {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "fiso-api",
                "namespace": self.namespace,
                "labels": {
                    "app": "fiso-api",
                    "tier": "backend"
                }
            },
            "spec": {
                "replicas": config.replicas,
                "selector": {
                    "matchLabels": {
                        "app": "fiso-api"
                    }
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": "fiso-api",
                            "tier": "backend"
                        }
                    },
                    "spec": {
                        "containers": [
                            {
                                "name": "fiso-api",
                                "image": "fiso/api:latest",
                                "ports": [
                                    {
                                        "containerPort": 8000,
                                        "name": "http"
                                    }
                                ],
                                "env": [
                                    {
                                        "name": "DATABASE_URL",
                                        "valueFrom": {
                                            "secretKeyRef": {
                                                "name": "fiso-secrets",
                                                "key": "database-url"
                                            }
                                        }
                                    },
                                    {
                                        "name": "REDIS_URL",
                                        "valueFrom": {
                                            "secretKeyRef": {
                                                "name": "fiso-secrets",
                                                "key": "redis-url"
                                            }
                                        }
                                    }
                                ],
                                "resources": {
                                    "requests": {
                                        "memory": config.resources.get("memory_request", "1Gi"),
                                        "cpu": config.resources.get("cpu_request", "500m")
                                    },
                                    "limits": {
                                        "memory": config.resources.get("memory_limit", "2Gi"),
                                        "cpu": config.resources.get("cpu_limit", "1000m")
                                    }
                                },
                                "livenessProbe": {
                                    "httpGet": {
                                        "path": "/health",
                                        "port": 8000
                                    },
                                    "initialDelaySeconds": 60,
                                    "periodSeconds": 30,
                                    "timeoutSeconds": 10
                                },
                                "readinessProbe": {
                                    "httpGet": {
                                        "path": "/health",
                                        "port": 8000
                                    },
                                    "initialDelaySeconds": 30,
                                    "periodSeconds": 10,
                                    "timeoutSeconds": 5
                                }
                            }
                        ]
                    }
                }
            }
        }
    
    def generate_api_service(self) -> Dict[str, Any]:
        """Generate API service manifest"""
        return {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": "fiso-api-service",
                "namespace": self.namespace,
                "labels": {
                    "app": "fiso-api"
                }
            },
            "spec": {
                "selector": {
                    "app": "fiso-api"
                },
                "ports": [
                    {
                        "port": 80,
                        "targetPort": 8000,
                        "name": "http"
                    }
                ],
                "type": "ClusterIP"
            }
        }
    
    def generate_hpa(self) -> Dict[str, Any]:
        """Generate Horizontal Pod Autoscaler"""
        return {
            "apiVersion": "autoscaling/v2",
            "kind": "HorizontalPodAutoscaler",
            "metadata": {
                "name": "fiso-api-hpa",
                "namespace": self.namespace
            },
            "spec": {
                "scaleTargetRef": {
                    "apiVersion": "apps/v1",
                    "kind": "Deployment",
                    "name": "fiso-api"
                },
                "minReplicas": 2,
                "maxReplicas": 10,
                "metrics": [
                    {
                        "type": "Resource",
                        "resource": {
                            "name": "cpu",
                            "target": {
                                "type": "Utilization",
                                "averageUtilization": 70
                            }
                        }
                    },
                    {
                        "type": "Resource",
                        "resource": {
                            "name": "memory",
                            "target": {
                                "type": "Utilization",
                                "averageUtilization": 80
                            }
                        }
                    }
                ]
            }
        }
    
    def generate_ingress(self, domain: str) -> Dict[str, Any]:
        """Generate ingress manifest"""
        return {
            "apiVersion": "networking.k8s.io/v1",
            "kind": "Ingress",
            "metadata": {
                "name": "fiso-ingress",
                "namespace": self.namespace,
                "annotations": {
                    "kubernetes.io/ingress.class": "nginx",
                    "cert-manager.io/cluster-issuer": "letsencrypt-prod",
                    "nginx.ingress.kubernetes.io/rate-limit": "100",
                    "nginx.ingress.kubernetes.io/rate-limit-window": "1m"
                }
            },
            "spec": {
                "tls": [
                    {
                        "hosts": [domain],
                        "secretName": "fiso-tls"
                    }
                ],
                "rules": [
                    {
                        "host": domain,
                        "http": {
                            "paths": [
                                {
                                    "path": "/api",
                                    "pathType": "Prefix",
                                    "backend": {
                                        "service": {
                                            "name": "fiso-api-service",
                                            "port": {
                                                "number": 80
                                            }
                                        }
                                    }
                                },
                                {
                                    "path": "/",
                                    "pathType": "Prefix",
                                    "backend": {
                                        "service": {
                                            "name": "fiso-frontend-service",
                                            "port": {
                                                "number": 80
                                            }
                                        }
                                    }
                                }
                            ]
                        }
                    }
                ]
            }
        }
    
    def save_manifests(self, manifests: List[Dict[str, Any]], directory: str = "k8s/manifests"):
        """Save Kubernetes manifests to files"""
        os.makedirs(directory, exist_ok=True)
        
        for i, manifest in enumerate(manifests):
            kind = manifest.get("kind", f"manifest-{i}")
            name = manifest.get("metadata", {}).get("name", f"unnamed-{i}")
            filename = f"{directory}/{kind.lower()}-{name}.yaml"
            
            with open(filename, 'w') as f:
                yaml.dump(manifest, f, default_flow_style=False, indent=2)
            
            logger.info(f"Saved manifest: {filename}")

class DeploymentOrchestrator:
    """Orchestrates deployment across different environments"""
    
    def __init__(self, config_file: str = "config/deployment.yml"):
        self.config = self._load_config(config_file)
        self.docker_compose_gen = DockerComposeGenerator()
        self.k8s_gen = KubernetesManifestGenerator()
    
    def _load_config(self, config_file: str) -> Dict[str, Any]:
        """Load deployment configuration"""
        try:
            with open(config_file, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.warning("Deployment config not found, using defaults")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default deployment configuration"""
        return {
            "environments": {
                "production": {
                    "replicas": 3,
                    "resources": {
                        "memory_request": "1Gi",
                        "memory_limit": "2Gi",
                        "cpu_request": "500m",
                        "cpu_limit": "1000m"
                    },
                    "domain": "fiso.company.com",
                    "database": {
                        "type": "postgresql",
                        "replicas": 2,
                        "backup_enabled": True
                    }
                },
                "staging": {
                    "replicas": 2,
                    "resources": {
                        "memory_request": "512Mi",
                        "memory_limit": "1Gi",
                        "cpu_request": "250m",
                        "cpu_limit": "500m"
                    },
                    "domain": "staging-fiso.company.com"
                }
            }
        }
    
    async def deploy_docker_compose(self, environment: str = "production"):
        """Deploy using Docker Compose"""
        logger.info(f"Deploying with Docker Compose to {environment}")
        
        # Generate compose file
        compose_config = self.docker_compose_gen.generate_production_compose()
        compose_file = f"docker-compose.{environment}.yml"
        self.docker_compose_gen.save_compose_file(compose_config, compose_file)
        
        # Deploy
        try:
            # Pull latest images
            subprocess.run(["docker-compose", "-f", compose_file, "pull"], check=True)
            
            # Deploy services
            subprocess.run(["docker-compose", "-f", compose_file, "up", "-d"], check=True)
            
            logger.info(f"Docker Compose deployment to {environment} completed successfully")
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Docker Compose deployment failed: {e}")
            raise
    
    async def deploy_kubernetes(self, environment: str = "production"):
        """Deploy to Kubernetes"""
        logger.info(f"Deploying to Kubernetes environment: {environment}")
        
        env_config = self.config["environments"][environment]
        deployment_config = DeploymentConfig(
            environment=environment,
            replicas=env_config["replicas"],
            resources=env_config["resources"],
            secrets={},
            config_maps={}
        )
        
        # Generate manifests
        manifests = [
            self.k8s_gen.generate_namespace(),
            self.k8s_gen.generate_api_deployment(deployment_config),
            self.k8s_gen.generate_api_service(),
            self.k8s_gen.generate_hpa(),
            self.k8s_gen.generate_ingress(env_config["domain"])
        ]
        
        # Save manifests
        self.k8s_gen.save_manifests(manifests)
        
        # Apply manifests
        try:
            subprocess.run(["kubectl", "apply", "-f", "k8s/manifests/"], check=True)
            logger.info(f"Kubernetes deployment to {environment} completed successfully")
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Kubernetes deployment failed: {e}")
            raise
    
    async def rollback_deployment(self, environment: str, revision: Optional[str] = None):
        """Rollback deployment to previous version"""
        logger.info(f"Rolling back deployment in {environment}")
        
        try:
            if revision:
                subprocess.run([
                    "kubectl", "rollout", "undo", f"deployment/fiso-api",
                    f"--to-revision={revision}",
                    f"--namespace=fiso-{environment}"
                ], check=True)
            else:
                subprocess.run([
                    "kubectl", "rollout", "undo", f"deployment/fiso-api",
                    f"--namespace=fiso-{environment}"
                ], check=True)
            
            logger.info(f"Rollback completed successfully")
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Rollback failed: {e}")
            raise
    
    async def health_check(self, environment: str) -> Dict[str, Any]:
        """Check deployment health"""
        logger.info(f"Checking health for {environment}")
        
        try:
            # Check Kubernetes deployment status
            result = subprocess.run([
                "kubectl", "get", "deployment", "fiso-api",
                f"--namespace=fiso-{environment}",
                "-o", "json"
            ], capture_output=True, text=True, check=True)
            
            deployment_info = json.loads(result.stdout)
            
            return {
                "status": "healthy" if deployment_info["status"]["readyReplicas"] > 0 else "unhealthy",
                "replicas": {
                    "desired": deployment_info["spec"]["replicas"],
                    "ready": deployment_info["status"].get("readyReplicas", 0),
                    "available": deployment_info["status"].get("availableReplicas", 0)
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

def create_deployment_config_template():
    """Create deployment configuration template"""
    config = {
        "environments": {
            "production": {
                "replicas": 3,
                "resources": {
                    "memory_request": "1Gi",
                    "memory_limit": "2Gi",
                    "cpu_request": "500m",
                    "cpu_limit": "1000m"
                },
                "domain": "fiso.company.com",
                "database": {
                    "type": "postgresql",
                    "replicas": 2,
                    "backup_enabled": True
                },
                "monitoring": {
                    "enabled": True,
                    "grafana_domain": "grafana-fiso.company.com"
                }
            },
            "staging": {
                "replicas": 2,
                "resources": {
                    "memory_request": "512Mi",
                    "memory_limit": "1Gi",
                    "cpu_request": "250m",
                    "cpu_limit": "500m"
                },
                "domain": "staging-fiso.company.com"
            }
        }
    }
    
    os.makedirs("config", exist_ok=True)
    with open("config/deployment.yml", "w") as f:
        yaml.dump(config, f, default_flow_style=False, indent=2)
    
    logger.info("Created deployment configuration template")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="FISO Deployment Orchestrator")
    parser.add_argument("--action", choices=["deploy", "rollback", "health"], required=True)
    parser.add_argument("--environment", default="production")
    parser.add_argument("--platform", choices=["docker-compose", "kubernetes"], default="kubernetes")
    parser.add_argument("--revision", help="Revision number for rollback")
    
    args = parser.parse_args()
    
    # Create configuration template
    create_deployment_config_template()
    
    # Initialize orchestrator
    orchestrator = DeploymentOrchestrator()
    
    async def main():
        try:
            if args.action == "deploy":
                if args.platform == "docker-compose":
                    await orchestrator.deploy_docker_compose(args.environment)
                else:
                    await orchestrator.deploy_kubernetes(args.environment)
                    
            elif args.action == "rollback":
                await orchestrator.rollback_deployment(args.environment, args.revision)
                
            elif args.action == "health":
                health = await orchestrator.health_check(args.environment)
                print(json.dumps(health, indent=2))
                
        except Exception as e:
            logger.error(f"Deployment operation failed: {e}")
            exit(1)
    
    asyncio.run(main())