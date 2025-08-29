-- Update the policies table to support multi-cloud orchestration
-- This script adds columns for Azure and GCP URLs

-- Add new columns for Azure and GCP URLs
ALTER TABLE policies 
ADD COLUMN IF NOT EXISTS azure_url TEXT,
ADD COLUMN IF NOT EXISTS gcp_url TEXT;

-- Update the existing policy with sample URLs (replace with your actual URLs)
UPDATE policies 
SET 
    azure_url = 'https://your-azure-function-app.azurewebsites.net/api/HttpTriggerFunc',
    gcp_url = 'https://your-region-your-project.cloudfunctions.net/your-function-name'
WHERE name = 'default-cost-saver';

-- Insert additional policies for testing different cloud providers
INSERT INTO policies (name, default_provider, default_arn, azure_url, gcp_url, is_active) VALUES
('aws-first', 'aws', 'arn:aws:lambda:us-east-1:ACCOUNT_ID:function:fiso_sample_app_py', 
 'https://your-azure-function-app.azurewebsites.net/api/HttpTriggerFunc',
 'https://your-region-your-project.cloudfunctions.net/your-function-name', false),
 
('azure-first', 'azure', 'arn:aws:lambda:us-east-1:ACCOUNT_ID:function:fiso_sample_app_py',
 'https://your-azure-function-app.azurewebsites.net/api/HttpTriggerFunc',
 'https://your-region-your-project.cloudfunctions.net/your-function-name', false),
 
('gcp-first', 'gcp', 'arn:aws:lambda:us-east-1:ACCOUNT_ID:function:fiso_sample_app_py',
 'https://your-azure-function-app.azurewebsites.net/api/HttpTriggerFunc',
 'https://your-region-your-project.cloudfunctions.net/your-function-name', false);

-- Show the current policies
SELECT id, name, default_provider, 
       CASE WHEN LENGTH(default_arn) > 50 THEN LEFT(default_arn, 50) || '...' ELSE default_arn END as default_arn,
       CASE WHEN LENGTH(azure_url) > 50 THEN LEFT(azure_url, 50) || '...' ELSE azure_url END as azure_url,
       CASE WHEN LENGTH(gcp_url) > 50 THEN LEFT(gcp_url, 50) || '...' ELSE gcp_url END as gcp_url,
       is_active, created_at 
FROM policies 
ORDER BY created_at;
