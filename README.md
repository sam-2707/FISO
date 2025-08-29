# FISO: FinOps-Intelligent Serverless Orchestrator

FISO is a smart, multi-cloud orchestration engine designed to deploy and manage serverless workloads with a core focus on FinOps. It provides a unified control plane to intelligently route function invocations across AWS, Azure, and GCP based on user-defined policies.

The primary goal of FISO is to abstract away the complexity of multi-cloud deployments while actively optimizing for cloud spend, bringing the principles of financial accountability directly into the CI/CD pipeline.

## 🚀 Quick Start

**Want to see FISO in action? Get started in 3 commands:**

```powershell
# 1. Clone and enter the project
git clone https://github.com/sam-2707/fiso.git && cd fiso

# 2. Start Docker Desktop, then run the setup
.\scripts\setup_multicloud.ps1

# 3. Test multi-cloud orchestration
Invoke-RestMethod -Method POST -Uri http://localhost:8080/api/v1/orchestrate
```

**Switch between cloud providers instantly:**
```powershell
.\scripts\switch_provider.ps1 aws    # Use AWS Lambda
.\scripts\switch_provider.ps1 azure  # Use Azure Functions  
.\scripts\switch_provider.ps1 gcp    # Use Google Cloud Functions
```

**Run the interactive demo:**
```powershell
.\scripts\demo_multicloud.ps1
```

**Validate your setup:**
```powershell
.\scripts\validate_setup.ps1
```

## Core Features

-   **� Multi-Cloud Orchestration:** Seamlessly invoke functions across AWS Lambda, Azure Functions, and Google Cloud Functions
-   **�🎛️ Centralized API Control Plane:** Single API endpoint for all cloud providers with intelligent routing
-   **☁️ Multi-Cloud Abstraction Layer (MCAL):** Terraform-based infrastructure for consistent deployments
-   **🧠 Policy-Driven Routing:** Database-backed policy engine for dynamic provider selection
-   **💰 Cost Analysis:** Built-in tools for comparing pricing across cloud providers
-   **🤖 Predictive Engine Foundation:** Framework for ML-based routing optimization
-   **🐳 Containerized Environment:** Docker-based development and deployment
-   **⚡ Real-time Switching:** Instant provider switching via PowerShell scripts

## Key Capabilities

### Multi-Cloud Support
- **AWS Lambda**: Production-ready with ARN-based invocation
- **Azure Functions**: HTTP-based invocation with Linux runtime
- **Google Cloud Functions**: HTTP trigger with public access

### Intelligent Routing
- **Policy-Based**: Database-driven provider selection
- **Cost-Aware**: Integration with pricing APIs for cost optimization
- **Performance-Focused**: Response time tracking and optimization
- **Failure Resilience**: Automatic failover capabilities (planned)

### Management & Operations
- **Easy Switching**: One-command provider changes
- **Comprehensive Logging**: Full request/response tracking
- **Health Monitoring**: Container and service status monitoring  
- **Cost Analysis**: Real-time pricing data from cloud providers

## Architectural Overview

FISO consists of three main components:

1.  **Orchestrator API:** A Go-based API that serves as the user's entry point. It receives requests, queries the database for the active policy, and invokes the target serverless function on the appropriate cloud.
2.  **Multi-Cloud Abstraction Layer (MCAL):** A collection of Terraform configurations that define the serverless infrastructure on each cloud provider, ensuring consistency and enabling repeatable deployments.
3.  **Predictive Engine & Database:** A PostgreSQL database stores policies and historical data. This data will be used by a Python-based predictive engine to calculate the optimal deployment strategy.

## Technology Stack

-   **Backend:** Go (Golang)
-   **Predictive Engine:** Python
-   **Database:** PostgreSQL
-   **Infrastructure as Code:** Terraform
-   **Containerization:** Docker, Docker Compose
-   **Cloud Providers:**
    -   Amazon Web Services (AWS)
    -   Microsoft Azure
    -   Google Cloud Platform (GCP)

## Project Structure

```
fiso/
├── api/                # Go-based Orchestrator API source code
│   ├── cmd/
│   │   └── fiso_server/
│   └── ...
├── dashboard/          # (Future) UI for analytics and policy management
├── docs/               # Project documentation
├── mcal/               # Multi-Cloud Abstraction Layer
│   ├── functions/      # Serverless function source code
│   │   ├── sample_app/         (For AWS & Azure)
│   │   └── sample_app_gcp/     (For GCP)
│   └── terraform/      # Terraform configurations
│       ├── aws/
│       ├── azure/
│       └── gcp/
├── predictor/          # (Future) Python-based predictive engine
├── scripts/            # Helper and utility scripts
└── tests/              # Test suites
```

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
