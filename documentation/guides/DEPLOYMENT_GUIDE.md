# FISO Deployment Guide

## 🚀 Production Deployment Options

### Quick Production Start

```powershell
# 1. Production servers (recommended)
python production_server.py &
python real_time_server.py &

# 2. Enterprise dashboard
cd frontend && npm run build && npm start

# Access:
# - Frontend: http://localhost:3000
# - API: http://localhost:5000  
# - Real-time: http://localhost:5001
```

## 🐳 Docker Deployment

### Build and Run
```powershell
# Build all containers
docker-compose build

# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### Container Services
- **fiso-frontend**: React dashboard (port 3000)
- **fiso-backend**: Flask API server (port 5000)
- **fiso-realtime**: WebSocket server (port 5001)
- **fiso-redis**: Cache layer (port 6379)
- **fiso-prometheus**: Monitoring (port 9090)

## ☁️ Cloud Deployment

### AWS Lambda
```powershell
cd lambda
# Deploy function
aws lambda create-function --function-name fiso-api --runtime python3.9 --handler lambda_handler.lambda_handler --zip-file fileb://function.zip

# Update function
aws lambda update-function-code --function-name fiso-api --zip-file fileb://function.zip
```

### Kubernetes (EKS/AKS/GKE)
```powershell
# Deploy to cluster
kubectl apply -f k8s/fiso-deployment.yaml
kubectl apply -f k8s/fiso-service.yaml
kubectl apply -f k8s/fiso-ingress.yaml

# Check deployment
kubectl get pods -l app=fiso
kubectl get services fiso-service
```

### Azure Functions
```powershell
cd mcal/functions
func azure functionapp publish fiso-functions
```

## 🔧 Environment Configuration

### Production Environment Variables
```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/fiso_prod
REDIS_URL=redis://localhost:6379

# Security
SECRET_KEY=your-production-secret-key
JWT_SECRET=your-jwt-secret-key
API_RATE_LIMIT=1000

# Cloud Providers
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
AZURE_SUBSCRIPTION_ID=your-azure-id
AZURE_CLIENT_ID=your-azure-client-id
AZURE_CLIENT_SECRET=your-azure-secret
GCP_PROJECT_ID=your-gcp-project
GCP_SERVICE_KEY_PATH=/path/to/service-key.json

# Monitoring
PROMETHEUS_ENDPOINT=http://localhost:9090
LOG_LEVEL=INFO
ENABLE_METRICS=true
```

### SSL/TLS Configuration
```bash
# Enable HTTPS
SSL_CERT_PATH=/path/to/certificate.crt
SSL_KEY_PATH=/path/to/private.key
FORCE_HTTPS=true
```

## 📊 Monitoring Setup

### Prometheus Metrics
```yaml
# config/prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'fiso-api'
    static_configs:
      - targets: ['localhost:5000']
  - job_name: 'fiso-realtime'  
    static_configs:
      - targets: ['localhost:5001']
```

### Health Checks
```powershell
# Automated health monitoring
python scripts/health_checks.py --production

# Setup monitoring alerts
python scripts/setup_alerts.py
```

## 🔒 Security Hardening

### Production Security Checklist
- [ ] Change default secret keys
- [ ] Enable HTTPS/SSL
- [ ] Configure firewall rules
- [ ] Set up rate limiting
- [ ] Enable audit logging
- [ ] Configure CORS properly
- [ ] Set up backup procedures
- [ ] Enable monitoring alerts

### Firewall Configuration
```powershell
# Allow required ports
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS  
ufw allow 5000/tcp  # API
ufw allow 5001/tcp  # WebSocket
ufw enable
```

## 📈 Performance Optimization

### Database Optimization
```sql
-- Create indexes for better performance
CREATE INDEX idx_cost_data_timestamp ON cost_data(timestamp);
CREATE INDEX idx_cost_data_provider ON cost_data(provider);
CREATE INDEX idx_anomalies_severity ON anomalies(severity);
```

### Caching Strategy
```python
# Redis configuration
CACHE_TYPE = "redis"
CACHE_REDIS_URL = "redis://localhost:6379"
CACHE_DEFAULT_TIMEOUT = 300  # 5 minutes
```

### Load Balancing
```nginx
# nginx.conf
upstream fiso_backend {
    server 127.0.0.1:5000;
    server 127.0.0.1:5001;
    server 127.0.0.1:5002;
}

server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://fiso_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 🔄 CI/CD Pipeline

### GitHub Actions Workflow
```yaml
# .github/workflows/deploy.yml
name: Deploy FISO
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: pip install -r requirements-production.txt
      - name: Run tests
        run: python -m pytest tests/
      - name: Deploy to production
        run: ./scripts/deploy.sh
```

### Automated Testing
```powershell
# Run full test suite before deployment
python -m pytest tests/ --cov=./ --cov-report=html

# Integration tests
python tests/test_integration.py --production

# Performance tests
python tests/test_performance.py --load-test
```

## 📦 Backup & Recovery

### Database Backup
```powershell
# Automated backup script
python scripts/backup_database.py --daily

# Restore from backup
python scripts/restore_database.py --file=backup_20240928.sql
```

### Configuration Backup
```powershell
# Backup all config files
tar -czf config_backup_$(date +%Y%m%d).tar.gz config/ .env security/
```

## 🚨 Troubleshooting

### Common Production Issues

1. **Port Already in Use**
```powershell
# Find and kill process
netstat -ano | findstr :5000
taskkill /PID <process_id> /F
```

2. **Database Connection Issues**
```powershell
# Test database connection
python -c "from sqlalchemy import create_engine; engine = create_engine('your_db_url'); print(engine.execute('SELECT 1').scalar())"
```

3. **Memory Issues**
```powershell
# Monitor memory usage
python scripts/monitor_resources.py --memory

# Optimize memory usage
python scripts/optimize_memory.py
```

4. **SSL Certificate Issues**
```powershell
# Verify certificate
openssl x509 -in certificate.crt -text -noout

# Renew certificate (Let's Encrypt)
certbot renew --nginx
```

### Performance Troubleshooting
```powershell
# Check API response times
python scripts/benchmark_api.py

# Monitor database queries
python scripts/monitor_db_performance.py

# Check memory leaks
python scripts/memory_profiler.py
```

## 📋 Maintenance Tasks

### Daily Tasks
- Monitor system health
- Check error logs
- Verify backup completion
- Review performance metrics

### Weekly Tasks
- Update dependencies
- Review security logs
- Performance optimization
- Capacity planning review

### Monthly Tasks
- Security audit
- Database maintenance
- Update documentation
- Disaster recovery test

## 🎯 Scaling Strategies

### Horizontal Scaling
```powershell
# Add new server instances
docker-compose scale fiso-backend=3 fiso-realtime=2

# Load balancer configuration
kubectl scale deployment fiso-deployment --replicas=5
```

### Vertical Scaling
```powershell
# Increase container resources
docker update --memory=2g --cpus=2 fiso-backend

# Optimize database performance
python scripts/optimize_database.py --production
```

## 📞 Support & Maintenance

### Monitoring Dashboards
- **Grafana**: http://localhost:3001
- **Prometheus**: http://localhost:9090
- **Application Logs**: `/logs/production.log`

### Emergency Contacts
- **System Administrator**: admin@company.com
- **Development Team**: dev-team@company.com
- **On-call Engineer**: +1-xxx-xxx-xxxx

### Service Level Agreements
- **Uptime**: 99.9% availability
- **Response Time**: <200ms average
- **Recovery Time**: <4 hours for critical issues
- **Data Retention**: 2 years historical data

---

**🚀 Your FISO production deployment is now ready for enterprise use!**

For additional support, visit our [documentation](/docs/) or contact the development team.