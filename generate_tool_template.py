#!/usr/bin/env python3
"""
Tool Template Generator for AWS FinOps MCP Server

This script generates boilerplate code for new FinOps tools based on templates.
Usage: python generate_tool_template.py <tool_name> <module_name> <tool_id>
"""

import sys
from pathlib import Path


TOOL_TEMPLATE = '''def {function_name}(
    session: Any,
    region_name: str,
    period: int = 90,
    max_results: int = 100
) -> dict[str, Any]:
    """{description}
    
    Args:
        session: Boto3 session
        region_name: AWS region name
        period: Lookback period in days
        max_results: Maximum results to return
    
    Returns:
        Dictionary with {resource_type}
    """
    {client_name}_client = session.client("{aws_service}", region_name=region_name)
    
    output_data = []
    
    logger.info(f"Finding {resource_type} in {{region_name}}")
    
    try:
        # TODO: Implement tool logic
        # 1. Get resources from AWS API
        # 2. Filter based on criteria
        # 3. Calculate costs if applicable
        # 4. Format output data
        
        # Example structure:
        # response = {client_name}_client.describe_{resource_type}(MaxResults=max_results)
        # for resource in response["{ResourceKey}"]:
        #     # Process each resource
        #     output_data.append({{
        #         "ResourceId": resource["Id"],
        #         "ResourceName": resource["Name"],
        #         # ... more fields
        #     }})
        
        # Calculate total savings if applicable
        total_monthly_cost = 0.0
        # total_monthly_cost = sum(
        #     float(item["EstimatedMonthlyCost"].replace("$", ""))
        #     for item in output_data
        # )
        
        fields = {{
            "1": "ResourceId",
            "2": "ResourceName",
            "3": "Description",
            # TODO: Add more fields
        }}
        
        result = {{
            "id": {tool_id},
            "name": "{display_name}",
            "fields": fields,
            "headers": fields_to_headers(fields),
            "count": len(output_data),
            "resource": output_data,
        }}
        
        # Add total cost if applicable
        if total_monthly_cost > 0:
            result["total_monthly_cost"] = f"${{total_monthly_cost:.2f}}"
        
        return result
        
    except Exception as e:
        logger.error(f"Error finding {resource_type}: {{e}}")
        raise
'''

SERVER_ENDPOINT_TEMPLATE = '''@mcp.tool()
async def {function_name}(
    region_name: str = "us-east-1",
    period: int = 90,
    max_results: int = 100,
    profile_name: str | None = None,
    role_arn: str | None = None,
    access_key: str | None = None,
    secret_access_key: str | None = None,
    session_token: str | None = None,
) -> dict[str, Any]:
    """{description}"""
    session = get_aws_session(
        profile_name, role_arn, access_key, secret_access_key, session_token
    )
    return {module_name}.{function_name}(session, region_name, period, max_results)
'''

TEST_TEMPLATE = '''def test_{function_name}():
    """Test {function_name} function."""
    # TODO: Implement test
    # Use moto for mocking AWS services
    # Example:
    # @mock_ec2
    # def test_function():
    #     session = boto3.Session()
    #     result = {function_name}(session, "us-east-1")
    #     assert result["count"] >= 0
    pass
'''


def generate_tool(tool_name: str, module_name: str, tool_id: int):
    """Generate tool template code."""
    
    # Convert tool_name to function_name (snake_case)
    function_name = tool_name.lower().replace(" ", "_").replace("-", "_")
    
    # Generate display name
    display_name = tool_name.title()
    
    # Infer AWS service and resource type from function name
    if "nat_gateway" in function_name:
        aws_service = "ec2"
        client_name = "ec2"
        resource_type = "NAT Gateways"
    elif "vpc_endpoint" in function_name:
        aws_service = "ec2"
        client_name = "ec2"
        resource_type = "VPC Endpoints"
    elif "s3" in function_name:
        aws_service = "s3"
        client_name = "s3"
        resource_type = "S3 Buckets"
    elif "dynamodb" in function_name:
        aws_service = "dynamodb"
        client_name = "dynamodb"
        resource_type = "DynamoDB Tables"
    elif "lambda" in function_name:
        aws_service = "lambda"
        client_name = "lambda"
        resource_type = "Lambda Functions"
    elif "rds" in function_name:
        aws_service = "rds"
        client_name = "rds"
        resource_type = "RDS Instances"
    elif "sqs" in function_name:
        aws_service = "sqs"
        client_name = "sqs"
        resource_type = "SQS Queues"
    elif "sns" in function_name:
        aws_service = "sns"
        client_name = "sns"
        resource_type = "SNS Topics"
    elif "cloudwatch" in function_name:
        aws_service = "cloudwatch"
        client_name = "cloudwatch"
        resource_type = "CloudWatch Resources"
    else:
        aws_service = "ec2"
        client_name = "ec2"
        resource_type = "Resources"
    
    description = f"Find {resource_type.lower()} based on specified criteria."
    
    # Generate tool code
    tool_code = TOOL_TEMPLATE.format(
        function_name=function_name,
        description=description,
        resource_type=resource_type.lower(),
        client_name=client_name,
        aws_service=aws_service,
        tool_id=tool_id,
        display_name=display_name,
        ResourceKey=resource_type.replace(" ", "")
    )
    
    # Generate server endpoint code
    endpoint_code = SERVER_ENDPOINT_TEMPLATE.format(
        function_name=function_name,
        description=description,
        module_name=module_name
    )
    
    # Generate test code
    test_code = TEST_TEMPLATE.format(function_name=function_name)
    
    print("=" * 80)
    print(f"TOOL: {display_name}")
    print(f"Function: {function_name}")
    print(f"Module: {module_name}")
    print(f"ID: {tool_id}")
    print("=" * 80)
    print("\n### Add to src/aws_finops_mcp/tools/{}.py:\n".format(module_name))
    print(tool_code)
    print("\n### Add to src/aws_finops_mcp/server.py:\n")
    print(endpoint_code)
    print("\n### Add to tests/test_{}.py:\n".format(module_name))
    print(test_code)
    print("\n" + "=" * 80)


def main():
    if len(sys.argv) < 4:
        print("Usage: python generate_tool_template.py <tool_name> <module_name> <tool_id>")
        print("\nExample:")
        print("  python generate_tool_template.py 'find_unused_sqs_queues' 'messaging' 210")
        sys.exit(1)
    
    tool_name = sys.argv[1]
    module_name = sys.argv[2]
    tool_id = int(sys.argv[3])
    
    generate_tool(tool_name, module_name, tool_id)


if __name__ == "__main__":
    main()
