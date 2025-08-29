#!/bin/bash

# Script to get deployment URLs from all cloud providers
# Run this from the project root directory

echo "=================================================="
echo "FISO Multi-Cloud Deployment URLs"
echo "=================================================="

echo ""
echo "🟢 AWS Lambda URLs:"
echo "--------------------------------------------------"
cd mcal/terraform/aws
if [ -f terraform.tfstate ]; then
    echo "Lambda ARN:"
    terraform output -raw lambda_arn 2>/dev/null || echo "❌ No AWS ARN found"
    echo ""
    echo "Lambda Invoke URL:"
    terraform output -raw lambda_invoke_url 2>/dev/null || echo "❌ No AWS URL found"
else
    echo "❌ No AWS deployment found (terraform.tfstate missing)"
fi

echo ""
echo "🔵 Azure Function URLs:"
echo "--------------------------------------------------"
cd ../azure
if [ -f terraform.tfstate ]; then
    echo "Function App Name:"
    terraform output -raw function_app_name 2>/dev/null || echo "❌ No Azure Function App name found"
    echo ""
    echo "Function App Invoke URL:"
    terraform output -raw function_app_invoke_url 2>/dev/null || echo "❌ No Azure URL found"
else
    echo "❌ No Azure deployment found (terraform.tfstate missing)"
fi

echo ""
echo "🟡 Google Cloud Function URLs:"
echo "--------------------------------------------------"
cd ../gcp
if [ -f terraform.tfstate ]; then
    echo "Function Name:"
    terraform output -raw function_name 2>/dev/null || echo "❌ No GCP Function name found"
    echo ""
    echo "Function Invoke URL:"
    terraform output -raw function_invoke_url 2>/dev/null || echo "❌ No GCP URL found"
else
    echo "❌ No GCP deployment found (terraform.tfstate missing)"
fi

echo ""
echo "=================================================="
echo "Next Steps:"
echo "1. Copy the URLs above"
echo "2. Update the database using scripts/update_policies_schema.sql"
echo "3. Replace placeholder URLs with actual deployment URLs"
echo "4. Restart the FISO API to use multi-cloud routing"
echo "=================================================="

cd ../../..
