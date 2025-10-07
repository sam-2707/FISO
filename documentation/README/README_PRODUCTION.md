# FISO Production Deployment

## Quick Start

1. **Configure Environment**:
   ```bash
   cp configs/environments/.env.template .env
   # Edit .env with your production values
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements-production.txt
   npm install
   ```

3. **Setup Cloud Credentials**:
   ```bash
   python scripts/setup/setup_real_data.py
   ```

4. **Deploy**:
   ```bash
   python scripts/deployment/deploy_production.py
   ```

## Production Endpoints

- **Main API**: http://your-domain:8000
- **Frontend**: http://your-domain:3000
- **Health Check**: http://your-domain:8000/health
- **API Documentation**: http://your-domain:8000/docs

## Directory Structure

```
fiso/
├── api/                    # Core API services
├── frontend/              # React frontend application
├── backend/               # Backend services
├── predictor/             # AI/ML engines
├── security/              # Security and authentication
├── configs/               # Configuration files
│   ├── environments/      # Environment configurations
│   └── production/        # Production-specific configs
├── scripts/               # Utility scripts
│   ├── deployment/        # Deployment scripts
│   ├── setup/            # Setup and initialization
│   └── maintenance/       # Maintenance utilities
├── docs/                  # Documentation
│   ├── production/        # Production documentation
│   ├── api/              # API documentation
│   └── deployment/        # Deployment guides
├── archive/               # Legacy and archived files
└── logs/                  # Log files
```

## Support

For production support, check:
- `docs/production/PRODUCTION_READINESS_CHECKLIST.md`
- `docs/deployment/DEPLOYMENT_GUIDE.md`
