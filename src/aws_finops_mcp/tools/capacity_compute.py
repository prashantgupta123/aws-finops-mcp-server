"""Compute capacity analysis tools for AWS resources."""

import logging
from datetime import datetime, timedelta
from typing import Any

from ..utils.helpers import fields_to_headers

logger = logging.getLogger(__name__)


def find_underutilized_lambda_functions(
    session: Any, region_name: str, period: int = 30
) -> dict[str, Any]:
    """Find Lambda functions with low invocation rates or high error rates.
    
    Args:
        session: Boto3 session
        region_name: AWS region name
        period: Lookback period in days
    
    Returns:
        Dictionary with underutilized Lambda functions
    """
    lambda_client = session.client("lambda", region_name=region_name)
    cloudwatch_client = session.client("cloudwatch", region_name=region_name)
    
    start_time = datetime.now() - timedelta(days=period)
    end_time = datetime.now()
    output_data = []
    
    logger.info(f"Finding underutilized Lambda functions in {region_name}")
    
    try:
        # Get all Lambda functions
        paginator = lambda_client.get_paginator("list_functions")
        
        for page in paginator.paginate():
            for function in page["Functions"]:
                function_name = function["FunctionName"]
                function_arn = function["FunctionArn"]
                
                # Check invocation count
                invocation_metric = cloudwatch_client.get_metric_statistics(
                    Namespace="AWS/Lambda",
                    MetricName="Invocations",
                    Dimensions=[{"Name": "FunctionName", "Value": function_name}],
                    StartTime=start_time,
                    EndTime=end_time,
                    Period=86400,
                    Statistics=["Sum"]
                )
                
                total_invocations = 0
                if invocation_metric["Datapoints"]:
                    total_invocations = sum(dp["Sum"] for dp in invocation_metric["Datapoints"])
                
                # Check error count
                error_metric = cloudwatch_client.get_metric_statistics(
                    Namespace="AWS/Lambda",
                    MetricName="Errors",
                    Dimensions=[{"Name": "FunctionName", "Value": function_name}],
                    StartTime=start_time,
                    EndTime=end_time,
                    Period=86400,
                    Statistics=["Sum"]
                )
                
                total_errors = 0
                if error_metric["Datapoints"]:
                    total_errors = sum(dp["Sum"] for dp in error_metric["Datapoints"])
                
                error_rate = (total_errors / total_invocations * 100) if total_invocations > 0 else 0
                
                # Flag if very low invocations or high error rate
                is_underutilized = total_invocations < 100 or error_rate > 50
                
                if is_underutilized:
                    runtime = function.get("Runtime", "N/A")
                    memory_size = function.get("MemorySize", 0)
                    timeout = function.get("Timeout", 0)
                    last_modified = function.get("LastModified", "N/A")
                    
                    # Get tags
                    tags = {}
                    try:
                        tags_response = lambda_client.list_tags(Resource=function_arn)
                        tags = tags_response.get("Tags", {})
                    except Exception:
                        pass
                    
                    # Estimate cost (very rough)
                    estimated_monthly_cost = (total_invocations / period * 30) * 0.0000002  # Rough estimate
                    
                    recommendation = "Consider removing if unused"
                    if error_rate > 50:
                        recommendation = "High error rate - investigate and fix or remove"
                    
                    output_data.append({
                        "FunctionName": function_name,
                        "FunctionArn": function_arn,
                        "Runtime": runtime,
                        "MemorySize": f"{memory_size} MB",
                        "Timeout": f"{timeout} seconds",
                        "TotalInvocations": int(total_invocations),
                        "TotalErrors": int(total_errors),
                        "ErrorRate": f"{error_rate:.2f}%",
                        "EstimatedMonthlyCost": f"${estimated_monthly_cost:.4f}",
                        "LastModified": last_modified,
                        "Tags": str(tags),
                        "Recommendation": recommendation,
                    })
        
        total_monthly_cost = sum(
            float(item["EstimatedMonthlyCost"].replace("$", ""))
            for item in output_data
        )
        
        fields = {
            "1": "FunctionName",
            "2": "Runtime",
            "3": "MemorySize",
            "4": "TotalInvocations",
            "5": "TotalErrors",
            "6": "ErrorRate",
            "7": "EstimatedMonthlyCost",
            "8": "LastModified",
            "9": "Recommendation",
            "10": "FunctionArn",
            "11": "Tags",
        }
        
        return {
            "id": 221,
            "name": "Underutilized Lambda Functions",
            "fields": fields,
            "headers": fields_to_headers(fields),
            "count": len(output_data),
            "total_monthly_cost": f"${total_monthly_cost:.2f}",
            "resource": output_data,
        }
        
    except Exception as e:
        logger.error(f"Error finding underutilized Lambda functions: {e}")
        raise
