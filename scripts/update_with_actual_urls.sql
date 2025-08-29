-- Update the policies table with actual deployment URLs
-- Run this in your PostgreSQL database after connecting with Docker

-- Add new columns for Azure and GCP URLs if they don't exist
ALTER TABLE policies 
ADD COLUMN IF NOT EXISTS azure_url TEXT,
ADD COLUMN IF NOT EXISTS gcp_url TEXT;

-- Update the existing policy with actual URLs from your deployments
UPDATE policies 
SET 
    azure_url = 'https://fiso-sample-function-app-cmcks5.azurewebsites.net/api/HttpTriggerFunc',
    gcp_url = 'https://us-central1-isentropic-button-hn4q7.cloudfunctions.net/fiso-sample-function-gcp'
WHERE name = 'default-cost-saver';

-- Insert additional policies for testing different cloud providers
INSERT INTO policies (name, default_provider, default_arn, azure_url, gcp_url, is_active) VALUES
('aws-first', 'aws', 'arn:aws:lambda:us-east-1:412374076384:function:fiso_sample_app_py', 
 'https://fiso-sample-function-app-cmcks5.azurewebsites.net/api/HttpTriggerFunc',
 'https://us-central1-isentropic-button-hn4q7.cloudfunctions.net/fiso-sample-function-gcp', false)
ON CONFLICT (name) DO UPDATE SET
    default_provider = EXCLUDED.default_provider,
    default_arn = EXCLUDED.default_arn,
    azure_url = EXCLUDED.azure_url,
    gcp_url = EXCLUDED.gcp_url;

INSERT INTO policies (name, default_provider, default_arn, azure_url, gcp_url, is_active) VALUES
('azure-first', 'azure', 'arn:aws:lambda:us-east-1:412374076384:function:fiso_sample_app_py',
 'https://fiso-sample-function-app-cmcks5.azurewebsites.net/api/HttpTriggerFunc',
 'https://us-central1-isentropic-button-hn4q7.cloudfunctions.net/fiso-sample-function-gcp', false)
ON CONFLICT (name) DO UPDATE SET
    default_provider = EXCLUDED.default_provider,
    default_arn = EXCLUDED.default_arn,
    azure_url = EXCLUDED.azure_url,
    gcp_url = EXCLUDED.gcp_url;

INSERT INTO policies (name, default_provider, default_arn, azure_url, gcp_url, is_active) VALUES
('gcp-first', 'gcp', 'arn:aws:lambda:us-east-1:412374076384:function:fiso_sample_app_py',
 'https://fiso-sample-function-app-cmcks5.azurewebsites.net/api/HttpTriggerFunc',
 'https://us-central1-isentropic-button-hn4q7.cloudfunctions.net/fiso-sample-function-gcp', false)
ON CONFLICT (name) DO UPDATE SET
    default_provider = EXCLUDED.default_provider,
    default_arn = EXCLUDED.default_arn,
    azure_url = EXCLUDED.azure_url,
    gcp_url = EXCLUDED.gcp_url;

-- Show the current policies
SELECT id, name, default_provider, 
       CASE WHEN LENGTH(default_arn) > 50 THEN LEFT(default_arn, 50) || '...' ELSE default_arn END as aws_arn,
       CASE WHEN LENGTH(azure_url) > 50 THEN LEFT(azure_url, 50) || '...' ELSE azure_url END as azure_url,
       CASE WHEN LENGTH(gcp_url) > 50 THEN LEFT(gcp_url, 50) || '...' ELSE gcp_url END as gcp_url,
       is_active, created_at 
FROM policies 
ORDER BY created_at;

-- Instructions for switching active policies:
-- To switch to Azure as the primary provider:
-- UPDATE policies SET is_active = false WHERE is_active = true;
-- UPDATE policies SET is_active = true WHERE name = 'azure-first';

-- To switch to GCP as the primary provider:
-- UPDATE policies SET is_active = false WHERE is_active = true;
-- UPDATE policies SET is_active = true WHERE name = 'gcp-first';

-- To switch back to AWS:
-- UPDATE policies SET is_active = false WHERE is_active = true;
-- UPDATE policies SET is_active = true WHERE name = 'aws-first';
