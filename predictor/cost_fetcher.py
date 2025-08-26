import boto3
import json

# This dictionary maps the region code to the name the Pricing API expects.
region_map = {
    "us-east-1": "US East (N. Virginia)",
    "us-east-2": "US East (Ohio)",
    "us-west-1": "US West (N. California)",
    "us-west-2": "US West (Oregon)",
    "ca-central-1": "Canada (Central)",
    "eu-west-1": "EU (Ireland)",
    "eu-central-1": "EU (Frankfurt)",
    "eu-west-2": "EU (London)",
    "ap-south-1": "Asia Pacific (Mumbai)",
    "ap-northeast-2": "Asia Pacific (Seoul)",
    "ap-southeast-1": "Asia Pacific (Singapore)",
    "ap-southeast-2": "Asia Pacific (Sydney)",
    "ap-northeast-1": "Asia Pacific (Tokyo)",
    "sa-east-1": "South America (Sao Paulo)",
}

def get_lambda_pricing(region_code="us-east-1"):
    """
    Fetches AWS Lambda pricing data for a specific region using the correct location name.
    """
    try:
        # Get the full location name from the map.
        location_name = region_map.get(region_code)
        if not location_name:
            print(f"Error: Region code '{region_code}' is not mapped to a location name.")
            return None

        pricing_client = boto3.client("pricing", region_name="us-east-1")

        print(f"Searching for Lambda pricing in: {location_name}...")

        # --- Get cost per million invocations ---
        response_invocations = pricing_client.get_products(
            ServiceCode="AWSLambda",
            Filters=[
                {"Type": "TERM_MATCH", "Field": "group", "Value": "AWS-Lambda-Requests"},
                # Use the corrected location name in the filter.
                {"Type": "TERM_MATCH", "Field": "location", "Value": location_name},
            ],
        )

        if not response_invocations["PriceList"]:
            print(f"Error: No pricing data found for Lambda Invocations in '{location_name}'.")
            return None

        price_data_invocations = json.loads(response_invocations["PriceList"][0])
        price_per_invocation = float(
            list(
                list(price_data_invocations["terms"]["OnDemand"].values())[0]["priceDimensions"].values()
            )[0]["pricePerUnit"]["USD"]
        )

        # --- Get cost per GB-second of duration ---
        response_duration = pricing_client.get_products(
            ServiceCode="AWSLambda",
            Filters=[
                {"Type": "TERM_MATCH", "Field": "group", "Value": "AWS-Lambda-Duration"},
                # Use the corrected location name in the filter.
                {"Type": "TERM_MATCH", "Field": "location", "Value": location_name},
            ],
        )

        if not response_duration["PriceList"]:
            print(f"Error: No pricing data found for Lambda Duration in '{location_name}'.")
            return None

        price_data_duration = json.loads(response_duration["PriceList"][0])
        price_per_gb_second = float(
            list(
                list(price_data_duration["terms"]["OnDemand"].values())[0]["priceDimensions"].values()
            )[0]["pricePerUnit"]["USD"]
        )

        print(f"\n--- AWS Lambda Pricing for: {location_name} ---")
        print(f"Cost per Invocation: ${price_per_invocation:.8f}")
        print(f"Cost per Million Invocations: ${price_per_invocation * 1_000_000:.2f}")
        print(f"Cost per GB-Second: ${price_per_gb_second:.9f}")
        
        return {
            "region": location_name,
            "invocation_cost": price_per_invocation,
            "gb_second_cost": price_per_gb_second
        }

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

if __name__ == "__main__":
    get_lambda_pricing(region_code="us-east-1")