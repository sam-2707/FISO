# FISO: FinOps-Intelligent Serverless Orchestrator

FISO is a complete enterprise-grade multi-cloud orchestration platform with integrated security, interactive dashboards, and professional CLI tools. It provides intelligent routing across AWS Lambda, Azure Functions, and Google Cloud Functions with comprehensive DevOps capabilities.

## 🎉 **PRODUCTION STATUS: FULLY OPERATIONAL**
- **✅ Multi-Cloud Orchestration**: 100% operational across all providers
- **✅ Enterprise Security**: JWT & API key authentication with rate limiting
- **✅ Interactive Dashboard**: Real-time monitoring and management interface
- **✅ Professional CLI**: Command-line toolkit for DevOps workflows
- **✅ Container Orchestration**: Docker and Kubernetes deployment ready

## 🚀 **Quick Start**

### Option 1: Interactive Dashboard (Recommended)
```powershell
# 1. Clone and setup
git clone https://github.com/sam-2707/fiso.git && cd fiso

# 2. Start the secure API server
cd security && python secure_server.py

# 3. Open interactive dashboard
# Navigate to: http://localhost:8080/secure_dashboard.html
```

### Option 2: Professional CLI
```powershell
# 1. Setup CLI tools
.\cli\setup_cli.ps1

# 2. Authenticate
.\cli\fiso.cmd auth login

# 3. Monitor system status
.\cli\fiso.cmd status

# 4. Real-time monitoring
.\cli\fiso.cmd watch
```

### Option 3: Traditional Multi-Cloud Setup
```powershell
# Traditional container-based setup
.\scripts\setup_multicloud.ps1
.\scripts\demo_multicloud.ps1
```

## 🏗️ **Core Features**

### **🔒 Enterprise Security System**
- **JWT & API Key Authentication**: Dual authentication methods with token generation
- **Rate Limiting**: IP-based and user-based request throttling  
- **Request Validation**: Schema validation and security headers
- **Permission System**: Role-based access control (RBAC)
- **Security Monitoring**: Real-time threat detection and audit logs

### **📊 Interactive Dashboard**
- **Real-time Monitoring**: Live provider health and performance metrics
- **Security Management**: API key generation and JWT token management
- **Performance Charts**: Historical performance data with Chart.js
- **API Testing**: Built-in testing interface for all endpoints
- **Responsive Design**: Mobile-friendly with modern UI/UX

### **⚡ Professional CLI Tools**
- **Multi-Command Interface**: Comprehensive argparse-based CLI
- **Authentication Management**: Secure login and configuration storage
- **Real-time Monitoring**: Live system status with colored output
- **Provider Operations**: Health checks and orchestration commands
- **Configuration Management**: User-specific settings and persistence

### **☁️ Multi-Cloud Orchestration**
- **AWS Lambda**: Production deployment with native SDK integration
- **Azure Functions**: HTTP-based invocation with Linux runtime
- **Google Cloud Functions**: Local emulator with production-ready config
- **Intelligent Routing**: Policy-based provider selection with failover
- **Performance Tracking**: Response time monitoring and optimization

### **🐳 Container & Kubernetes Support**
- **Docker Compose**: Complete containerized development environment
- **Kubernetes Deployment**: Production-ready K8s manifests and scripts
- **AWS EKS Integration**: Automated cluster setup and monitoring
- **CI/CD Ready**: GitHub Actions and automated deployment pipelines

## 🎯 **Deployment Status**

### **✅ Production Ready Components**
- **Secure API Server**: `http://localhost:5000` - Enterprise authentication & routing
- **Interactive Dashboard**: `http://localhost:8080/secure_dashboard.html` - Real-time monitoring
- **CLI Tools**: `.\cli\fiso.cmd` - Professional command-line interface
- **AWS Lambda**: `https://krls9u88od.execute-api.us-east-1.amazonaws.com/prod` - Fully operational
- **Azure Functions**: `https://fiso-sample-function-app-cmcks5.azurewebsites.net/api/httptriggerfunc` - Deployed
- **GCP Emulator**: `http://localhost:8080` - Local development ready

### **🔧 Infrastructure Components**
- **Multi-Cloud Abstraction Layer (MCAL)**: Terraform configurations for all providers
- **Database Integration**: PostgreSQL with policy management
- **Container Orchestration**: Docker Compose for local development
- **Kubernetes Support**: Production-ready manifests and automation
- **Security Layer**: JWT authentication, rate limiting, and audit logging

## 🏛️ **Architecture Overview**

FISO follows a modern microservices architecture with enterprise security:

### **1. Secure API Gateway**
- **Flask-based Server**: Enterprise-grade Python web server with CORS support
- **Authentication Layer**: JWT and API key validation with session management
- **Rate Limiting**: IP-based and user-based request throttling
- **Request Routing**: Intelligent provider selection and failover logic

### **2. Interactive Dashboard**
- **Web Interface**: Responsive HTML5 dashboard with real-time updates
- **Performance Monitoring**: Chart.js integration for metrics visualization
- **Security Management**: Built-in API key generation and testing tools
- **Activity Logging**: Real-time audit logs and security monitoring

### **3. Professional CLI**
- **Command Interface**: Argparse-based CLI with colored output
- **Configuration Management**: User-specific settings and authentication
- **Real-time Monitoring**: Live system status and health checks
- **Automation Ready**: Scriptable commands for CI/CD integration

### **4. Multi-Cloud Abstraction Layer (MCAL)**
- **Terraform Infrastructure**: Consistent deployments across all providers
- **Provider SDKs**: Native integration with AWS, Azure, and GCP APIs
- **Policy Engine**: Database-driven routing and configuration management
- **Container Support**: Docker and Kubernetes orchestration

## 💻 **Technology Stack**

### **Backend & Security**
- **Python 3.11+**: Secure API server with Flask and enterprise authentication
- **Go (Golang)**: High-performance orchestrator API with cloud provider SDKs
- **PostgreSQL**: Policy engine and configuration database
- **JWT & API Keys**: Dual authentication with role-based permissions

### **Frontend & Interfaces**
- **HTML5/CSS3/JavaScript**: Interactive dashboard with real-time updates
- **Chart.js**: Performance metrics and monitoring visualizations
- **Python CLI**: Professional command-line tools with argparse
- **PowerShell Scripts**: Windows automation and deployment tools

### **Infrastructure & DevOps**
- **Docker & Docker Compose**: Containerized development environment
- **Kubernetes**: Production-ready orchestration with monitoring
- **Terraform**: Infrastructure as Code for all cloud providers
- **GitHub Actions**: CI/CD pipelines and automated deployments

### **Cloud Providers & Services**
- **Amazon Web Services (AWS)**: Lambda, API Gateway, CloudWatch
- **Microsoft Azure**: Functions, App Service, Container Instances
- **Google Cloud Platform (GCP)**: Cloud Functions, Cloud Run, Cloud Build

## 📁 **Project Structure**

```
fiso/
├── security/                    # 🔒 Enterprise Security System
│   ├── fiso_security.py        # Core security manager with JWT/API keys
│   ├── secure_api.py           # Multi-cloud API gateway
│   └── secure_server.py        # Flask web server with authentication
├── dashboard/                   # 📊 Interactive Web Dashboard
│   ├── secure_dashboard.html   # Main dashboard interface
│   └── index.html              # Legacy dashboard
├── cli/                        # ⚡ Professional CLI Tools
│   ├── fiso.py                 # Main CLI application
│   ├── fiso.cmd                # Windows batch launcher
│   ├── setup_cli.ps1           # CLI installation script
│   └── demo_cli.ps1            # CLI demonstration
├── api/                        # 🔧 Go-based Orchestrator API
│   ├── cmd/fiso_server/        # Main server application
│   └── ...                     # API source code
├── mcal/                       # ☁️ Multi-Cloud Abstraction Layer
│   ├── functions/              # Serverless function deployments
│   │   ├── sample_app/         # Azure Functions deployment
│   │   └── sample_app_gcp/     # Google Cloud Functions
│   └── terraform/              # Infrastructure as Code
├── scripts/                    # 🤖 Automation & Management
│   ├── setup_multicloud.ps1   # Multi-cloud environment setup
│   ├── demo_multicloud.ps1    # Interactive demonstrations
│   ├── switch_provider.ps1    # Provider switching automation
│   └── ...                     # Additional automation scripts
├── k8s/                        # 🚢 Kubernetes Deployment
│   ├── fiso-deployment.yaml   # Application deployment manifests
│   ├── fiso-monitoring.yaml   # Monitoring and observability
│   └── ...                     # Kubernetes configurations
├── security/                   # 🛡️ Security & Authentication
├── predictor/                  # 🧠 Cost Intelligence Engine
├── lambda/                     # 🔷 AWS Lambda Functions
├── terraform/                  # 🏗️ Infrastructure as Code
└── docs/                       # 📖 Documentation & Guides
```

## 🎮 **Usage Examples**

### **Interactive Dashboard Usage**
```powershell
# 1. Start the secure API server
cd security
python secure_server.py

# 2. Open dashboard in browser
# Visit: http://localhost:8080/secure_dashboard.html

# 3. Generate API key in dashboard or use demo key
# Demo API Key: fiso_DbL7ElzVfdJdabE... (generated on startup)
```

### **CLI Usage Examples**
```powershell
# Setup and authentication
.\cli\fiso.cmd auth login                    # Authenticate with FISO API
.\cli\fiso.cmd config show                   # View current configuration

# Monitoring and status
.\cli\fiso.cmd status                        # Get comprehensive system status
.\cli\fiso.cmd health                        # Check all provider health
.\cli\fiso.cmd health --provider aws         # Check specific provider
.\cli\fiso.cmd metrics                       # View performance metrics

# Operations and orchestration
.\cli\fiso.cmd orchestrate                   # Auto-select best provider
.\cli\fiso.cmd orchestrate --provider azure  # Use specific provider
.\cli\fiso.cmd watch                         # Real-time monitoring

# Help and documentation
.\cli\fiso.cmd --help                        # Show all available commands
.\cli\fiso.cmd health --help                 # Command-specific help
```

### **API Integration Examples**
```bash
# Health check with API key
curl -H "X-API-Key: fiso_your_api_key" \
     http://localhost:5000/health

# Multi-cloud orchestration
curl -X POST \
     -H "X-API-Key: fiso_your_api_key" \
     -H "Content-Type: application/json" \
     -d '{"provider": "aws", "region": "us-east-1"}' \
     http://localhost:5000/orchestrate

# Get system metrics (admin required)
curl -H "Authorization: Bearer your_jwt_token" \
     http://localhost:5000/metrics
```

## 🚀 **Getting Started**

### **Prerequisites**
- **Python 3.11+** - For security server and CLI tools
- **Docker Desktop** - For container orchestration (optional)
- **PowerShell 5.1+** - For automation scripts  
- **Cloud Provider Access** - AWS, Azure, or GCP credentials

### **Quick Setup (Recommended)**
```powershell
# 1. Clone repository
git clone https://github.com/sam-2707/fiso.git
cd fiso

# 2. Setup Python environment
python -m venv .venv
.\.venv\Scripts\activate
pip install flask flask-cors PyJWT requests cryptography

# 3. Start secure API server
cd security
python secure_server.py

# 4. Open interactive dashboard
# Visit: http://localhost:8080/secure_dashboard.html
```

### **CLI Tools Setup**
```powershell
# Setup CLI tools
.\cli\setup_cli.ps1

# Start using CLI
.\cli\fiso.cmd auth login
.\cli\fiso.cmd status
```

### **Traditional Multi-Cloud Setup**
```powershell
# For full container-based setup
.\scripts\setup_multicloud.ps1
.\scripts\demo_multicloud.ps1
```

## 📚 **Documentation**

### **Core Documentation**
- **[📊 Status Report](STATUS_REPORT.md)** - Current implementation status and metrics
- **[🗺️ Development Roadmap](ROADMAP.md)** - Future enhancement phases and planning
- **[🔧 Azure Fix Status](AZURE_FIX_STATUS.md)** - Azure Functions integration details

### **Technical Guides**
- **[📖 Production Enhancement Guide](docs/FISO_Production_Enhancement_Guide.ipynb)** - Jupyter notebook with detailed examples
- **[🔒 Security Documentation](security/)** - Enterprise security implementation details
- **[⚡ CLI Reference](cli/)** - Command-line interface documentation
- **[🌐 API Documentation](http://localhost:5000/docs)** - Interactive API documentation (when server is running)

### **Quick References**
- **Interactive Dashboard**: `http://localhost:8080/secure_dashboard.html`
- **Secure API Server**: `http://localhost:5000`
- **CLI Commands**: `.\cli\fiso.cmd --help`
- **Container Setup**: `.\scripts\setup_multicloud.ps1`

## 🤝 **Contributing**

### **Development Setup**
```powershell
# Clone and setup development environment
git clone https://github.com/sam-2707/fiso.git
cd fiso

# Setup Python environment
python -m venv .venv
.\.venv\Scripts\activate
pip install -r security/requirements.txt

# Setup CLI tools
.\cli\setup_cli.ps1

# Start development server
cd security && python secure_server.py
```

### **Testing**
```powershell
# Run comprehensive tests
.\scripts\validate_setup.ps1

# Test specific components
.\cli\fiso.cmd health
.\scripts\demo_secure_api.ps1
.\scripts\demo_multicloud.ps1
```

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 **Acknowledgments**

- **AWS, Azure, GCP** - Multi-cloud provider integration
- **Flask & Python Community** - Web framework and security libraries
- **Chart.js** - Interactive dashboard visualization
- **Docker & Kubernetes** - Container orchestration platforms

---

**FISO: Making multi-cloud orchestration simple, secure, and scalable.**

## Getting Started

Follow these instructions to get a local instance of the FISO multi-cloud orchestrator running and deploy sample functions to AWS, Azure, and GCP.

### Prerequisites

Ensure you have the following tools installed and configured on your system:

-   Git
-   **Docker Desktop** (with Docker Compose)
-   Go (version 1.21+)
-   Python (version 3.9+)
-   Terraform (latest version)
-   Cloud CLIs:
    -   AWS CLI (run `aws configure`)
    -   Azure CLI (run `az login`)
    -   Google Cloud CLI (run `gcloud auth login` and `gcloud auth application-default login`)

### Quick Start (Recommended)

**🚀 For the fastest setup, use our automated multi-cloud setup script:**

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/sam-2707/fiso.git
    cd fiso
    ```

2.  **Start Docker Desktop** and ensure it's running

3.  **Run the Multi-Cloud Setup:**
    ```powershell
    # Windows PowerShell
    .\scripts\setup_multicloud.ps1
    ```
    
    This script will:
    - Start all Docker containers
    - Set up the PostgreSQL database
    - Configure multi-cloud policies
    - Test all cloud providers

4.  **Switch Between Cloud Providers:**
    ```powershell
    # Switch to AWS Lambda
    .\scripts\switch_provider.ps1 aws
    
    # Switch to Azure Functions
    .\scripts\switch_provider.ps1 azure
    
    # Switch to Google Cloud Functions
    .\scripts\switch_provider.ps1 gcp
    ```

5.  **Test the Orchestration:**
    ```powershell
    Invoke-RestMethod -Method POST -Uri http://localhost:8080/api/v1/orchestrate
    ```

6.  **Run Interactive Demo:**
    ```powershell
    .\scripts\demo_multicloud.ps1
    ```

### Manual Setup (Advanced)

If you prefer to set up everything manually or need to deploy cloud functions:

#### Step 1: Deploy Cloud Functions

**Deploy to AWS:**
```bash
cd mcal/terraform/aws
terraform init
terraform apply --auto-approve
```

**Deploy to Azure:**
```bash
cd ../azure
terraform init
terraform apply --auto-approve
```

**Deploy to GCP:**
- Set your `gcp_project_id` in `mcal/terraform/gcp/variables.tf`
- Create a service account with `Owner` role and save the JSON key as `gcp-credentials.json`
```bash
cd ../gcp
terraform init
terraform apply --auto-approve
```

#### Step 2: Get Deployment URLs
```powershell
.\scripts\get_deployment_urls.ps1
```

#### Step 3: Start Local Environment
```bash
# Start Docker containers
docker-compose up --build -d
```

#### Step 4: Configure Database
```powershell
# Update database with your actual URLs
Get-Content "scripts\update_with_actual_urls.sql" | docker exec -i fiso_db psql -U fiso -d fiso_db
```

## Using FISO

### Basic Usage

Once FISO is running, you can interact with it through the API or management scripts:

#### Switch Cloud Providers
```powershell
# Switch to AWS Lambda (most cost-effective for small workloads)
.\scripts\switch_provider.ps1 aws

# Switch to Azure Functions (good for Microsoft ecosystem)
.\scripts\switch_provider.ps1 azure

# Switch to Google Cloud Functions (excellent for data processing)
.\scripts\switch_provider.ps1 gcp
```

#### Invoke Functions
```powershell
# Single invocation
Invoke-RestMethod -Method POST -Uri http://localhost:8080/api/v1/orchestrate

# Multiple invocations to test performance
1..5 | ForEach-Object { 
    Invoke-RestMethod -Method POST -Uri http://localhost:8080/api/v1/orchestrate 
}
```

#### View Logs
```bash
# View API logs
docker-compose logs api

# View database logs
docker-compose logs db

# Follow logs in real-time
docker-compose logs -f api
```

### Cost Analysis

FISO includes a cost analysis tool to help with cloud provider selection:

```powershell
# Analyze AWS Lambda pricing
python predictor/cost_fetcher.py
```

### Management Commands

```powershell
# Get deployment URLs from all cloud providers
.\scripts\get_deployment_urls.ps1

# Run interactive multi-cloud demo
.\scripts\demo_multicloud.ps1

# Stop all containers
docker-compose down

# Restart with fresh build
docker-compose down && docker-compose up --build -d

# Validate your setup
.\scripts\validate_setup.ps1
```

## API Reference

### Orchestration Endpoint

**POST** `/api/v1/orchestrate`

Invokes a serverless function on the currently active cloud provider based on the database policy.

**Example Request:**
```powershell
Invoke-RestMethod -Method POST -Uri http://localhost:8080/api/v1/orchestrate
```

**Example Response:**
```json
{
    "message": "Hello from the FISO Sample App!",
    "platform": "AWS Lambda",
    "python_version": "3.9.23",
    "provider": "aws",
    "status_code": 200
}
```

**Response varies by provider:**
- **AWS**: `"platform": "AWS Lambda"`
- **Azure**: `"platform": "Azure Functions"`
- **GCP**: `"platform": "Google Cloud Functions"`

## Configuration

### Database Policies

FISO uses PostgreSQL to store routing policies. Each policy defines which cloud provider to use:

```sql
-- View current policies
SELECT id, name, default_provider, is_active FROM policies ORDER BY created_at;

-- Switch to AWS
UPDATE policies SET is_active = false WHERE is_active = true;
UPDATE policies SET is_active = true WHERE name = 'aws-first';

-- Switch to Azure  
UPDATE policies SET is_active = false WHERE is_active = true;
UPDATE policies SET is_active = true WHERE name = 'azure-first';

-- Switch to GCP
UPDATE policies SET is_active = false WHERE is_active = true;
UPDATE policies SET is_active = true WHERE name = 'gcp-first';
```

### Environment Variables

FISO API requires the following environment variable:

- `DATABASE_URL`: PostgreSQL connection string (automatically set in Docker Compose)

## Troubleshooting

### Common Issues

**1. Docker containers not starting:**
```bash
# Check Docker Desktop is running
docker ps

# Restart containers
docker-compose down && docker-compose up --build -d
```

**2. Database connection errors:**
```bash
# Check database is running
docker-compose logs db

# Reconnect to database
docker exec -it fiso_db psql -U fiso -d fiso_db
```

**3. Cloud function errors (404/403):**
```bash
# Verify deployments
.\scripts\get_deployment_urls.ps1

# Check Terraform state
cd mcal/terraform/aws && terraform output
cd ../azure && terraform output  
cd ../gcp && terraform output
```

**4. API not responding:**
```bash
# Check API logs
docker-compose logs api

# Restart API
docker-compose restart api
```

### Logs and Debugging

```bash
# View all logs
docker-compose logs

# Follow specific service logs
docker-compose logs -f api
docker-compose logs -f db

# Check container status
docker-compose ps
```

## Architecture

FISO's multi-cloud architecture consists of:

### Components
1. **Go API Server**: Handles orchestration requests and routing logic
2. **PostgreSQL Database**: Stores policies and routing configuration  
3. **Multi-Cloud Functions**: Identical Python functions deployed across AWS, Azure, and GCP
4. **Policy Engine**: Database-driven intelligent routing system
5. **Cost Analyzer**: Python tool for pricing analysis across cloud providers

### Flow
```
User Request → FISO API → Policy Engine → Cloud Provider Selection → Function Invocation → Response
```

### Cloud Provider Support
- ✅ **AWS Lambda**: Fully functional with ARN-based invocation
- ⚠️ **Azure Functions**: HTTP-based invocation (deployment dependent)
- ⚠️ **Google Cloud Functions**: HTTP-based invocation (deployment dependent)

## Roadmap

FISO continues to evolve with these planned enhancements:

### Completed ✅
- [x] Multi-cloud orchestration framework
- [x] Policy-driven routing system
- [x] AWS Lambda integration
- [x] Database-backed configuration
- [x] Cost analysis foundation
- [x] Docker containerization
- [x] Management scripts and automation

### In Progress 🚧
- [ ] **Complete Azure & GCP Deployments**: Fix deployment issues and verify URLs
- [ ] **Enhanced Cost Analysis**: Integration of cost data into routing decisions
- [ ] **Performance Metrics**: Latency and response time tracking
- [ ] **Real-time Monitoring**: Dashboard for function performance and costs

### Future Enhancements 🔮
- [ ] **Advanced Policy Engine**: Rules based on cost, latency, region, and workload type
- [ ] **Predictive Analytics**: ML-based routing optimization
- [ ] **Auto-scaling Logic**: Dynamic resource allocation
- [ ] **Web Dashboard**: UI for policy management and analytics
- [ ] **Multi-region Support**: Geographic distribution and failover
- [ ] **CI/CD Integration**: Automated deployment pipelines

## Contributing

We welcome contributions to FISO! Here's how you can help:

### Areas for Contribution
- **Cloud Provider Integrations**: Enhance Azure and GCP deployments
- **Cost Optimization**: Improve the predictive engine
- **Monitoring & Observability**: Add metrics and logging
- **Documentation**: Improve setup guides and API documentation
- **Testing**: Add unit and integration tests

### Getting Started
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests if applicable
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

---

**🌐 FISO: Making multi-cloud serverless orchestration simple, intelligent, and cost-effective.**
