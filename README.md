# FISO: FinOps-Intelligent Serverless Orchestrator

FISO is a smart, multi-cloud orchestration engine designed to deploy and manage serverless workloads with a core focus on FinOps. It provides a unified control plane to intelligently route function invocations across AWS, Azure, and GCP based on user-defined policies.

The primary goal of FISO is to abstract away the complexity of multi-cloud deployments while actively optimizing for cloud spend, bringing the principles of financial accountability directly into the CI/CD pipeline.

## Core Features

-   **🎛️ Centralized API Control Plane:** A single API endpoint to invoke serverless functions, regardless of where they are deployed.
-   **☁️ Multi-Cloud Abstraction Layer (MCAL):** Uses Terraform to define and deploy identical function workloads across AWS Lambda, Azure Functions, and Google Cloud Functions.
-   **🧠 Policy-Driven Orchestration:** A database-backed policy engine that allows administrators to define routing rules.
-   **🤖 Predictive Engine (In Development):** A future component designed to analyze real-time pricing, performance metrics, and historical data to make automated, intelligent routing decisions.
-   **🐳 Containerized Environment:** The entire local development environment is managed with Docker and Docker Compose for consistency and ease of setup.

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

Follow these instructions to get a local instance of the FISO orchestrator running and deploy the sample function to AWS and GCP.

### Prerequisites

Ensure you have the following tools installed and configured on your system:

-   Git
-   Docker & Docker Compose
-   Go (version 1.21+)
-   Python (version 3.9+)
-   Terraform (latest version)
-   Cloud CLIs:
    -   AWS CLI (run `aws configure`)
    -   Azure CLI (run `az login`)
    -   Google Cloud CLI (run `gcloud auth login` and `gcloud auth application-default login`)

### Installation & Deployment

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/your-username/fiso.git
    cd fiso
    ```

2.  **Deploy to AWS:**
    Navigate to the AWS Terraform directory.
    ```bash
    cd mcal/terraform/aws
    ```
    Initialize and apply the configuration.
    ```bash
    terraform init
    terraform apply --auto-approve
    ```
    Take note of the `lambda_arn` from the output.

3.  **Deploy to GCP:**
    -   **Important:** Open `mcal/terraform/gcp/variables.tf` and set your `gcp_project_id`.
    -   **Important:** Follow the GCP documentation to create a service account with the `Owner` role. Download its JSON key and save it as `gcp-credentials.json` inside the `mcal/terraform/gcp/` directory.

    Navigate to the GCP Terraform directory.
    ```bash
    cd ../gcp
    ```
    Initialize and apply the configuration.
    ```bash
    terraform init -upgrade
    terraform apply --auto-approve
    ```

4.  **Set Up the Local Environment:**
    Navigate to the project root.
    ```bash
    cd ../../../  # Back to root fiso/ directory
    ```
    Start the Docker containers.
    ```bash
    docker-compose up --build
    ```

5.  **Configure the Database:**
    While the containers are running, open a new terminal.
    Connect to the PostgreSQL database.
    ```bash
    docker exec -it fiso_db psql -U fiso -d fiso_db
    ```
    Create the `policies` table and insert a default policy. Remember to replace the placeholder ARN with your actual AWS Lambda ARN.
    ```sql
    CREATE TABLE policies (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL UNIQUE,
        default_provider VARCHAR(50) NOT NULL,
        default_arn TEXT NOT NULL,
        is_active BOOLEAN DEFAULT true,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );

    INSERT INTO policies (name, default_provider, default_arn) VALUES
    ('default-cost-saver', 'aws', 'arn:aws:lambda:us-east-1:ACCOUNT_ID:function:fiso_sample_app_py');
    ```
    Exit psql:
    ```
    \q
    ```

## API Usage

Once everything is running, you can interact with the FISO orchestrator via its API endpoint. The orchestrator will read your policy from the database and invoke the function on AWS.

Send a POST request to the orchestrator:
```powershell
# PowerShell example
Invoke-RestMethod -Method POST -Uri http://localhost:8080/api/v1/orchestrate
```
```bash
# cURL example
curl -X POST http://localhost:8080/api/v1/orchestrate
```

**Expected Response:**
```json
{
    "message": "Hello from the FISO Sample App!",
    "platform": "AWS Lambda",
    "python_version": "3.9.x"
}
```

## Roadmap

FISO is under active development. Our future plans include:

-   [ ] Complete Azure Deployment: Finalize and test the Azure Functions deployment.
-   [ ] Build the Predictive Engine: Develop the Python service to analyze cloud costs and performance.
-   [ ] Advanced Policy Management: Enhance the policy engine to support rules based on performance (latency), region, and real-time cost.
-   [ ] Multi-Cloud Invocation: Update the orchestrator to dynamically invoke functions on Azure and GCP.
-   [ ] Dashboard: Create a simple web interface to visualize costs, performance, and manage policies.

## Contributing

Contributions are welcome! If you'd like to help improve FISO, please feel free to fork the repository, make your changes, and submit a pull request.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
