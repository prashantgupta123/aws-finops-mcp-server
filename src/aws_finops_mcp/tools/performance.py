"""Performance analysis tools for AWS resources."""

import logging
from datetime import datetime, timedelta
from typing import Any

from ..utils.helpers import fields_to_headers

logger = logging.getLogger(__name__)


def analyze_lambda_cold_starts(
    session: Any, region_name: str, period: int = 7
) -> dict[str, Any]:
    """Analyze Lambda functions for cold start issues.
    
    Args:
        session: Boto3 session
        region_name: AWS region name
        period: Lookback period in days
    
    Returns:
        Dictionary with Lambda cold start analysis
    """
    lambda_client = session.client("lambda", region_name=region_name)
    cloudwatch_client = session.client("cloudwatch", region_name=region_name)
    logs_client = session.client("logs", region_name=region_name)
    
    output_data = []
    
    logger.info(f"Analyzing Lambda cold starts in {region_name}")
    
    try:
        # Get all Lambda functions
        paginator = lambda_client.get_paginator("list_functions")
        
        start_time = datetime.now() - timedelta(days=period)
        end_time = datetime.now()
        
        for page in paginator.paginate():
            for function in page["Functions"]:
                function_name = function["FunctionName"]
                function_arn = function["FunctionArn"]
                runtime = function.get("Runtime", "N/A")
                memory_size = function.get("MemorySize", 0)
                timeout = function.get("Timeout", 0)
                
                # Check duration metrics
                duration_metric = cloudwatch_client.get_metric_statistics(
                    Namespace="AWS/Lambda",
                    MetricName="Duration",
                    Dimensions=[{"Name": "FunctionName", "Value": function_name}],
                    StartTime=start_time,
                    EndTime=end_time,
                    Period=86400,
                    Statistics=["Average", "Maximum"]
                )
                
                if duration_metric["Datapoints"]:
                    avg_duration = sum(dp["Average"] for dp in duration_metric["Datapoints"]) / len(duration_metric["Datapoints"])
                    max_duration = max(dp["Maximum"] for dp in duration_metric["Datapoints"])
                    
                    # High variance suggests cold starts
                    duration_variance = max_duration - avg_duration
                    has_cold_start_issue = duration_variance > 1000  # > 1 second variance
                    
                    if has_cold_start_issue:
                        # Get tags
                        tags = {}
                        try:
                            tags_response = lambda_client.list_tags(Resource=function_arn)
                            tags = tags_response.get("Tags", {})
                        except Exception:
                            pass
                        
                        recommendation = "Consider provisioned concurrency or increase memory"
                        if memory_size < 512:
                            recommendation = "Increase memory size to reduce cold starts"
                        
                        output_data.append({
                            "FunctionName": function_name,
                            "FunctionArn": function_arn,
                            "Runtime": runtime,
                            "MemorySize": f"{memory_size} MB",
                            "Timeout": f"{timeout} seconds",
                            "AverageDuration": f"{avg_duration:.2f} ms",
                            "MaxDuration": f"{max_duration:.2f} ms",
                            "DurationVariance": f"{duration_variance:.2f} ms",
                            "Tags": str(tags),
                            "Recommendation": recommendation,
                        })
        
        fields = {
            "1": "FunctionName",
            "2": "Runtime",
            "3": "MemorySize",
            "4": "AverageDuration",
            "5": "MaxDuration",
            "6": "DurationVariance",
            "7": "Recommendation",
            "8": "FunctionArn",
            "9": "Tags",
        }
        
        return {
            "id": 501,
            "name": "Lambda Cold Start Analysis",
            "fields": fields,
            "headers": fields_to_headers(fields),
            "count": len(output_data),
            "resource": output_data,
        }
        
    except Exception as e:
        logger.error(f"Error analyzing Lambda cold starts: {e}")
        raise


def analyze_api_gateway_performance(
    session: Any, region_name: str, period: int = 7
) -> dict[str, Any]:
    """Analyze API Gateway performance metrics.
    
    Args:
        session: Boto3 session
        region_name: AWS region name
        period: Lookback period in days
    
    Returns:
        Dictionary with API Gateway performance analysis
    """
    apigateway_client = session.client("apigateway", region_name=region_name)
    cloudwatch_client = session.client("cloudwatch", region_name=region_name)
    
    output_data = []
    
    logger.info(f"Analyzing API Gateway performance in {region_name}")
    
    try:
        # Get all REST APIs
        apis_response = apigateway_client.get_rest_apis()
        
        start_time = datetime.now() - timedelta(days=period)
        end_time = datetime.now()
        
        for api in apis_response.get("items", []):
            api_id = api["id"]
            api_name = api["name"]
            
            # Check latency
            latency_metric = cloudwatch_client.get_metric_statistics(
                Namespace="AWS/ApiGateway",
                MetricName="Latency",
                Dimensions=[{"Name": "ApiName", "Value": api_name}],
                StartTime=start_time,
                EndTime=end_time,
                Period=86400,
                Statistics=["Average", "Maximum"]
            )
            
            # Check 4XX and 5XX errors
            error_4xx_metric = cloudwatch_client.get_metric_statistics(
                Namespace="AWS/ApiGateway",
                MetricName="4XXError",
                Dimensions=[{"Name": "ApiName", "Value": api_name}],
                StartTime=start_time,
                EndTime=end_time,
                Period=86400,
                Statistics=["Sum"]
            )
            
            error_5xx_metric = cloudwatch_client.get_metric_statistics(
                Namespace="AWS/ApiGateway",
                MetricName="5XXError",
                Dimensions=[{"Name": "ApiName", "Value": api_name}],
                StartTime=start_time,
                EndTime=end_time,
                Period=86400,
                Statistics=["Sum"]
            )
            
            if latency_metric["Datapoints"]:
                avg_latency = sum(dp["Average"] for dp in latency_metric["Datapoints"]) / len(latency_metric["Datapoints"])
                max_latency = max(dp["Maximum"] for dp in latency_metric["Datapoints"])
                
                total_4xx = sum(dp["Sum"] for dp in error_4xx_metric["Datapoints"]) if error_4xx_metric["Datapoints"] else 0
                total_5xx = sum(dp["Sum"] for dp in error_5xx_metric["Datapoints"]) if error_5xx_metric["Datapoints"] else 0
                
                # Flag if high latency or errors
                has_performance_issue = avg_latency > 1000 or total_5xx > 100
                
                if has_performance_issue:
                    # Get tags
                    tags_response = apigateway_client.get_tags(resourceArn=f"arn:aws:apigateway:{region_name}::/restapis/{api_id}")
                    tags = tags_response.get("tags", {})
                    
                    recommendation = ""
                    if avg_latency > 1000:
                        recommendation = "High latency - optimize backend integrations or enable caching"
                    if total_5xx > 100:
                        recommendation += " High 5XX errors - investigate backend issues"
                    
                    output_data.append({
                        "ApiId": api_id,
                        "ApiName": api_name,
                        "AverageLatency": f"{avg_latency:.2f} ms",
                        "MaxLatency": f"{max_latency:.2f} ms",
                        "Total4XXErrors": int(total_4xx),
                        "Total5XXErrors": int(total_5xx),
                        "Tags": str(tags),
                        "Recommendation": recommendation.strip(),
                    })
        
        fields = {
            "1": "ApiId",
            "2": "ApiName",
            "3": "AverageLatency",
            "4": "MaxLatency",
            "5": "Total4XXErrors",
            "6": "Total5XXErrors",
            "7": "Recommendation",
            "8": "Tags",
        }
        
        return {
            "id": 502,
            "name": "API Gateway Performance Analysis",
            "fields": fields,
            "headers": fields_to_headers(fields),
            "count": len(output_data),
            "resource": output_data,
        }
        
    except Exception as e:
        logger.error(f"Error analyzing API Gateway performance: {e}")
        raise


def analyze_dynamodb_throttling(
    session: Any, region_name: str, period: int = 7
) -> dict[str, Any]:
    """Analyze DynamoDB tables for throttling issues.
    
    Args:
        session: Boto3 session
        region_name: AWS region name
        period: Lookback period in days
    
    Returns:
        Dictionary with DynamoDB throttling analysis
    """
    dynamodb_client = session.client("dynamodb", region_name=region_name)
    cloudwatch_client = session.client("cloudwatch", region_name=region_name)
    
    output_data = []
    
    logger.info(f"Analyzing DynamoDB throttling in {region_name}")
    
    try:
        # Get all tables
        tables_response = dynamodb_client.list_tables()
        
        start_time = datetime.now() - timedelta(days=period)
        end_time = datetime.now()
        
        for table_name in tables_response.get("TableNames", []):
            # Check for throttled requests
            throttle_metric = cloudwatch_client.get_metric_statistics(
                Namespace="AWS/DynamoDB",
                MetricName="UserErrors",
                Dimensions=[{"Name": "TableName", "Value": table_name}],
                StartTime=start_time,
                EndTime=end_time,
                Period=86400,
                Statistics=["Sum"]
            )
            
            if throttle_metric["Datapoints"]:
                total_throttles = sum(dp["Sum"] for dp in throttle_metric["Datapoints"])
                
                if total_throttles > 0:
                    # Get table details
                    table_response = dynamodb_client.describe_table(TableName=table_name)
                    table = table_response["Table"]
                    
                    billing_mode = table.get("BillingModeSummary", {}).get("BillingMode", "PROVISIONED")
                    
                    output_data.append({
                        "TableName": table_name,
                        "TableArn": table["TableArn"],
                        "BillingMode": billing_mode,
                        "TotalThrottles": int(total_throttles),
                        "Recommendation": "Enable auto-scaling or switch to on-demand billing" if billing_mode == "PROVISIONED" else "Review access patterns",
                    })
        
        fields = {
            "1": "TableName",
            "2": "BillingMode",
            "3": "TotalThrottles",
            "4": "Recommendation",
            "5": "TableArn",
        }
        
        return {
            "id": 503,
            "name": "DynamoDB Throttling Analysis",
            "fields": fields,
            "headers": fields_to_headers(fields),
            "count": len(output_data),
            "resource": output_data,
        }
        
    except Exception as e:
        logger.error(f"Error analyzing DynamoDB throttling: {e}")
        raise


def analyze_rds_performance_insights(
    session: Any, region_name: str, period: int = 7
) -> dict[str, Any]:
    """Analyze RDS Performance Insights data.
    
    Args:
        session: Boto3 session
        region_name: AWS region name
        period: Lookback period in days
    
    Returns:
        Dictionary with RDS performance analysis
    """
    rds_client = session.client("rds", region_name=region_name)
    cloudwatch_client = session.client("cloudwatch", region_name=region_name)
    
    output_data = []
    
    logger.info(f"Analyzing RDS performance in {region_name}")
    
    try:
        # Get all DB instances
        paginator = rds_client.get_paginator("describe_db_instances")
        
        start_time = datetime.now() - timedelta(days=period)
        end_time = datetime.now()
        
        for page in paginator.paginate():
            for db_instance in page["DBInstances"]:
                db_instance_id = db_instance["DBInstanceIdentifier"]
                
                # Check CPU utilization
                cpu_metric = cloudwatch_client.get_metric_statistics(
                    Namespace="AWS/RDS",
                    MetricName="CPUUtilization",
                    Dimensions=[{"Name": "DBInstanceIdentifier", "Value": db_instance_id}],
                    StartTime=start_time,
                    EndTime=end_time,
                    Period=86400,
                    Statistics=["Average", "Maximum"]
                )
                
                if cpu_metric["Datapoints"]:
                    avg_cpu = sum(dp["Average"] for dp in cpu_metric["Datapoints"]) / len(cpu_metric["Datapoints"])
                    max_cpu = max(dp["Maximum"] for dp in cpu_metric["Datapoints"])
                    
                    if avg_cpu > 70 or max_cpu > 90:
                        output_data.append({
                            "DBInstanceIdentifier": db_instance_id,
                            "DBInstanceArn": db_instance["DBInstanceArn"],
                            "Engine": db_instance["Engine"],
                            "DBInstanceClass": db_instance["DBInstanceClass"],
                            "AverageCPU": f"{avg_cpu:.2f}%",
                            "MaxCPU": f"{max_cpu:.2f}%",
                            "Recommendation": "Consider scaling up instance class or optimizing queries",
                        })
        
        fields = {
            "1": "DBInstanceIdentifier",
            "2": "Engine",
            "3": "DBInstanceClass",
            "4": "AverageCPU",
            "5": "MaxCPU",
            "6": "Recommendation",
            "7": "DBInstanceArn",
        }
        
        return {
            "id": 504,
            "name": "RDS Performance Analysis",
            "fields": fields,
            "headers": fields_to_headers(fields),
            "count": len(output_data),
            "resource": output_data,
        }
        
    except Exception as e:
        logger.error(f"Error analyzing RDS performance: {e}")
        raise


def analyze_cloudfront_cache_hit_ratio(
    session: Any, region_name: str = "us-east-1", period: int = 7
) -> dict[str, Any]:
    """Analyze CloudFront cache hit ratios.
    
    Args:
        session: Boto3 session
        region_name: AWS region (CloudFront is global but uses us-east-1)
        period: Lookback period in days
    
    Returns:
        Dictionary with CloudFront cache analysis
    """
    cloudfront_client = session.client("cloudfront", region_name="us-east-1")
    cloudwatch_client = session.client("cloudwatch", region_name="us-east-1")
    
    output_data = []
    
    logger.info("Analyzing CloudFront cache hit ratios")
    
    try:
        # Get all distributions
        paginator = cloudfront_client.get_paginator("list_distributions")
        
        start_time = datetime.now() - timedelta(days=period)
        end_time = datetime.now()
        
        for page in paginator.paginate():
            for distribution in page.get("DistributionList", {}).get("Items", []):
                distribution_id = distribution["Id"]
                domain_name = distribution["DomainName"]
                
                # Check cache hit rate
                cache_hit_metric = cloudwatch_client.get_metric_statistics(
                    Namespace="AWS/CloudFront",
                    MetricName="CacheHitRate",
                    Dimensions=[{"Name": "DistributionId", "Value": distribution_id}],
                    StartTime=start_time,
                    EndTime=end_time,
                    Period=86400,
                    Statistics=["Average"]
                )
                
                if cache_hit_metric["Datapoints"]:
                    avg_cache_hit_rate = sum(dp["Average"] for dp in cache_hit_metric["Datapoints"]) / len(cache_hit_metric["Datapoints"])
                    
                    if avg_cache_hit_rate < 80:
                        recommendation = "Low cache hit rate - review cache behaviors and TTL settings"
                        
                        output_data.append({
                            "DistributionId": distribution_id,
                            "DomainName": domain_name,
                            "CacheHitRate": f"{avg_cache_hit_rate:.2f}%",
                            "Status": distribution["Status"],
                            "Recommendation": recommendation,
                        })
        
        fields = {
            "1": "DistributionId",
            "2": "DomainName",
            "3": "CacheHitRate",
            "4": "Status",
            "5": "Recommendation",
        }
        
        return {
            "id": 505,
            "name": "CloudFront Cache Hit Ratio Analysis",
            "fields": fields,
            "headers": fields_to_headers(fields),
            "count": len(output_data),
            "resource": output_data,
        }
        
    except Exception as e:
        logger.error(f"Error analyzing CloudFront cache hit ratios: {e}")
        raise
