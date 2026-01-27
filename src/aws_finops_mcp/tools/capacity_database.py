"""Database capacity analysis tools for AWS resources."""

import logging
from datetime import datetime, timedelta
from typing import Any

from ..utils.helpers import fields_to_headers

logger = logging.getLogger(__name__)


def find_overutilized_dynamodb_tables(
    session: Any, region_name: str, period: int = 30
) -> dict[str, Any]:
    """Find DynamoDB tables with high capacity utilization (>80%).
    
    Args:
        session: Boto3 session
        region_name: AWS region name
        period: Lookback period in days
    
    Returns:
        Dictionary with overutilized DynamoDB tables
    """
    dynamodb_client = session.client("dynamodb", region_name=region_name)
    cloudwatch_client = session.client("cloudwatch", region_name=region_name)
    
    start_time = datetime.now() - timedelta(days=period)
    end_time = datetime.now()
    output_data = []
    
    logger.info(f"Finding overutilized DynamoDB tables in {region_name}")
    
    try:
        # Get all tables
        tables_response = dynamodb_client.list_tables()
        
        for table_name in tables_response.get("TableNames", []):
            try:
                # Get table details
                table_response = dynamodb_client.describe_table(TableName=table_name)
                table = table_response["Table"]
                
                billing_mode = table.get("BillingModeSummary", {}).get("BillingMode", "PROVISIONED")
                
                # Only check provisioned tables
                if billing_mode != "PROVISIONED":
                    continue
                
                provisioned_read = table.get("ProvisionedThroughput", {}).get("ReadCapacityUnits", 0)
                provisioned_write = table.get("ProvisionedThroughput", {}).get("WriteCapacityUnits", 0)
                
                # Check CloudWatch metrics for utilization
                read_utilization = 0.0
                write_utilization = 0.0
                
                # Get consumed read capacity
                read_metric = cloudwatch_client.get_metric_statistics(
                    Namespace="AWS/DynamoDB",
                    MetricName="ConsumedReadCapacityUnits",
                    Dimensions=[{"Name": "TableName", "Value": table_name}],
                    StartTime=start_time,
                    EndTime=end_time,
                    Period=86400,  # 1 day
                    Statistics=["Average"]
                )
                
                if read_metric["Datapoints"]:
                    avg_consumed_read = sum(dp["Average"] for dp in read_metric["Datapoints"]) / len(read_metric["Datapoints"])
                    read_utilization = (avg_consumed_read / provisioned_read * 100) if provisioned_read > 0 else 0
                
                # Get consumed write capacity
                write_metric = cloudwatch_client.get_metric_statistics(
                    Namespace="AWS/DynamoDB",
                    MetricName="ConsumedWriteCapacityUnits",
                    Dimensions=[{"Name": "TableName", "Value": table_name}],
                    StartTime=start_time,
                    EndTime=end_time,
                    Period=86400,
                    Statistics=["Average"]
                )
                
                if write_metric["Datapoints"]:
                    avg_consumed_write = sum(dp["Average"] for dp in write_metric["Datapoints"]) / len(write_metric["Datapoints"])
                    write_utilization = (avg_consumed_write / provisioned_write * 100) if provisioned_write > 0 else 0
                
                # Flag if either read or write utilization > 80%
                if read_utilization > 80 or write_utilization > 80:
                    table_arn = table["TableArn"]
                    table_size_bytes = table.get("TableSizeBytes", 0)
                    item_count = table.get("ItemCount", 0)
                    
                    # Get tags
                    tags = {}
                    try:
                        tags_response = dynamodb_client.list_tags_of_resource(ResourceArn=table_arn)
                        tags = {tag["Key"]: tag["Value"] for tag in tags_response.get("Tags", [])}
                    except Exception:
                        pass
                    
                    output_data.append({
                        "TableName": table_name,
                        "TableArn": table_arn,
                        "BillingMode": billing_mode,
                        "ProvisionedReadCapacity": provisioned_read,
                        "ProvisionedWriteCapacity": provisioned_write,
                        "ReadUtilization": f"{read_utilization:.2f}%",
                        "WriteUtilization": f"{write_utilization:.2f}%",
                        "TableSizeGB": f"{table_size_bytes / (1024**3):.2f}",
                        "ItemCount": item_count,
                        "Tags": str(tags),
                        "Recommendation": "Increase provisioned capacity or enable auto-scaling",
                    })
            except Exception as e:
                logger.warning(f"Could not check table {table_name}: {e}")
                continue
        
        fields = {
            "1": "TableName",
            "2": "BillingMode",
            "3": "ProvisionedReadCapacity",
            "4": "ProvisionedWriteCapacity",
            "5": "ReadUtilization",
            "6": "WriteUtilization",
            "7": "TableSizeGB",
            "8": "ItemCount",
            "9": "Recommendation",
            "10": "TableArn",
            "11": "Tags",
        }
        
        return {
            "id": 217,
            "name": "Overutilized DynamoDB Tables",
            "fields": fields,
            "headers": fields_to_headers(fields),
            "count": len(output_data),
            "resource": output_data,
        }
        
    except Exception as e:
        logger.error(f"Error finding overutilized DynamoDB tables: {e}")
        raise


def find_underutilized_elasticache_clusters(
    session: Any, region_name: str, period: int = 30
) -> dict[str, Any]:
    """Find ElastiCache clusters with low CPU utilization (<20%).
    
    Args:
        session: Boto3 session
        region_name: AWS region name
        period: Lookback period in days
    
    Returns:
        Dictionary with underutilized ElastiCache clusters
    """
    elasticache_client = session.client("elasticache", region_name=region_name)
    cloudwatch_client = session.client("cloudwatch", region_name=region_name)
    
    start_time = datetime.now() - timedelta(days=period)
    end_time = datetime.now()
    output_data = []
    
    logger.info(f"Finding underutilized ElastiCache clusters in {region_name}")
    
    try:
        # Get all cache clusters
        paginator = elasticache_client.get_paginator("describe_cache_clusters")
        
        for page in paginator.paginate():
            for cluster in page["CacheClusters"]:
                cluster_id = cluster["CacheClusterId"]
                
                # Check CPU utilization
                cpu_metric = cloudwatch_client.get_metric_statistics(
                    Namespace="AWS/ElastiCache",
                    MetricName="CPUUtilization",
                    Dimensions=[{"Name": "CacheClusterId", "Value": cluster_id}],
                    StartTime=start_time,
                    EndTime=end_time,
                    Period=86400,
                    Statistics=["Average"]
                )
                
                if cpu_metric["Datapoints"]:
                    avg_cpu = sum(dp["Average"] for dp in cpu_metric["Datapoints"]) / len(cpu_metric["Datapoints"])
                    
                    if avg_cpu < 20:
                        cluster_arn = cluster["ARN"]
                        engine = cluster["Engine"]
                        engine_version = cluster["EngineVersion"]
                        cache_node_type = cluster["CacheNodeType"]
                        num_cache_nodes = cluster.get("NumCacheNodes", 0)
                        
                        # Estimate cost (rough estimate)
                        estimated_monthly_cost = num_cache_nodes * 50  # Rough estimate
                        
                        # Get tags
                        tags = {}
                        try:
                            tags_response = elasticache_client.list_tags_for_resource(ResourceName=cluster_arn)
                            tags = {tag["Key"]: tag["Value"] for tag in tags_response.get("TagList", [])}
                        except Exception:
                            pass
                        
                        output_data.append({
                            "CacheClusterId": cluster_id,
                            "CacheClusterArn": cluster_arn,
                            "Engine": engine,
                            "EngineVersion": engine_version,
                            "CacheNodeType": cache_node_type,
                            "NumCacheNodes": num_cache_nodes,
                            "AverageCPUUtilization": f"{avg_cpu:.2f}%",
                            "EstimatedMonthlyCost": f"${estimated_monthly_cost:.2f}",
                            "Tags": str(tags),
                            "Recommendation": "Consider downsizing or terminating cluster",
                        })
        
        total_monthly_cost = sum(
            float(item["EstimatedMonthlyCost"].replace("$", ""))
            for item in output_data
        )
        
        fields = {
            "1": "CacheClusterId",
            "2": "Engine",
            "3": "CacheNodeType",
            "4": "NumCacheNodes",
            "5": "AverageCPUUtilization",
            "6": "EstimatedMonthlyCost",
            "7": "Recommendation",
            "8": "CacheClusterArn",
            "9": "Tags",
        }
        
        return {
            "id": 218,
            "name": "Underutilized ElastiCache Clusters",
            "fields": fields,
            "headers": fields_to_headers(fields),
            "count": len(output_data),
            "total_monthly_cost": f"${total_monthly_cost:.2f}",
            "resource": output_data,
        }
        
    except Exception as e:
        logger.error(f"Error finding underutilized ElastiCache clusters: {e}")
        raise


def find_overutilized_elasticache_clusters(
    session: Any, region_name: str, period: int = 30
) -> dict[str, Any]:
    """Find ElastiCache clusters with high CPU or memory utilization (>80%).
    
    Args:
        session: Boto3 session
        region_name: AWS region name
        period: Lookback period in days
    
    Returns:
        Dictionary with overutilized ElastiCache clusters
    """
    elasticache_client = session.client("elasticache", region_name=region_name)
    cloudwatch_client = session.client("cloudwatch", region_name=region_name)
    
    start_time = datetime.now() - timedelta(days=period)
    end_time = datetime.now()
    output_data = []
    
    logger.info(f"Finding overutilized ElastiCache clusters in {region_name}")
    
    try:
        # Get all cache clusters
        paginator = elasticache_client.get_paginator("describe_cache_clusters")
        
        for page in paginator.paginate():
            for cluster in page["CacheClusters"]:
                cluster_id = cluster["CacheClusterId"]
                engine = cluster["Engine"]
                
                # Check CPU utilization
                cpu_metric = cloudwatch_client.get_metric_statistics(
                    Namespace="AWS/ElastiCache",
                    MetricName="CPUUtilization",
                    Dimensions=[{"Name": "CacheClusterId", "Value": cluster_id}],
                    StartTime=start_time,
                    EndTime=end_time,
                    Period=86400,
                    Statistics=["Average"]
                )
                
                avg_cpu = 0.0
                if cpu_metric["Datapoints"]:
                    avg_cpu = sum(dp["Average"] for dp in cpu_metric["Datapoints"]) / len(cpu_metric["Datapoints"])
                
                # Check memory utilization (metric name differs by engine)
                memory_metric_name = "DatabaseMemoryUsagePercentage" if engine == "redis" else "BytesUsedForCache"
                memory_metric = cloudwatch_client.get_metric_statistics(
                    Namespace="AWS/ElastiCache",
                    MetricName=memory_metric_name,
                    Dimensions=[{"Name": "CacheClusterId", "Value": cluster_id}],
                    StartTime=start_time,
                    EndTime=end_time,
                    Period=86400,
                    Statistics=["Average"]
                )
                
                avg_memory = 0.0
                if memory_metric["Datapoints"]:
                    avg_memory = sum(dp["Average"] for dp in memory_metric["Datapoints"]) / len(memory_metric["Datapoints"])
                
                if avg_cpu > 80 or avg_memory > 80:
                    cluster_arn = cluster["ARN"]
                    engine_version = cluster["EngineVersion"]
                    cache_node_type = cluster["CacheNodeType"]
                    num_cache_nodes = cluster.get("NumCacheNodes", 0)
                    
                    # Get tags
                    tags = {}
                    try:
                        tags_response = elasticache_client.list_tags_for_resource(ResourceName=cluster_arn)
                        tags = {tag["Key"]: tag["Value"] for tag in tags_response.get("TagList", [])}
                    except Exception:
                        pass
                    
                    output_data.append({
                        "CacheClusterId": cluster_id,
                        "CacheClusterArn": cluster_arn,
                        "Engine": engine,
                        "EngineVersion": engine_version,
                        "CacheNodeType": cache_node_type,
                        "NumCacheNodes": num_cache_nodes,
                        "AverageCPUUtilization": f"{avg_cpu:.2f}%",
                        "AverageMemoryUtilization": f"{avg_memory:.2f}%",
                        "Tags": str(tags),
                        "Recommendation": "Consider scaling up node type or adding nodes",
                    })
        
        fields = {
            "1": "CacheClusterId",
            "2": "Engine",
            "3": "CacheNodeType",
            "4": "NumCacheNodes",
            "5": "AverageCPUUtilization",
            "6": "AverageMemoryUtilization",
            "7": "Recommendation",
            "8": "CacheClusterArn",
            "9": "Tags",
        }
        
        return {
            "id": 219,
            "name": "Overutilized ElastiCache Clusters",
            "fields": fields,
            "headers": fields_to_headers(fields),
            "count": len(output_data),
            "resource": output_data,
        }
        
    except Exception as e:
        logger.error(f"Error finding overutilized ElastiCache clusters: {e}")
        raise


def find_underutilized_ecs_services(
    session: Any, region_name: str, period: int = 30
) -> dict[str, Any]:
    """Find ECS services with low CPU and memory utilization (<20%).
    
    Args:
        session: Boto3 session
        region_name: AWS region name
        period: Lookback period in days
    
    Returns:
        Dictionary with underutilized ECS services
    """
    ecs_client = session.client("ecs", region_name=region_name)
    cloudwatch_client = session.client("cloudwatch", region_name=region_name)
    
    start_time = datetime.now() - timedelta(days=period)
    end_time = datetime.now()
    output_data = []
    
    logger.info(f"Finding underutilized ECS services in {region_name}")
    
    try:
        # Get all clusters
        clusters_response = ecs_client.list_clusters()
        
        for cluster_arn in clusters_response.get("clusterArns", []):
            cluster_name = cluster_arn.split("/")[-1]
            
            # Get services in cluster
            services_response = ecs_client.list_services(cluster=cluster_arn)
            
            if not services_response.get("serviceArns"):
                continue
            
            # Describe services
            services_details = ecs_client.describe_services(
                cluster=cluster_arn,
                services=services_response["serviceArns"]
            )
            
            for service in services_details.get("services", []):
                service_name = service["serviceName"]
                
                # Check CPU utilization
                cpu_metric = cloudwatch_client.get_metric_statistics(
                    Namespace="AWS/ECS",
                    MetricName="CPUUtilization",
                    Dimensions=[
                        {"Name": "ServiceName", "Value": service_name},
                        {"Name": "ClusterName", "Value": cluster_name}
                    ],
                    StartTime=start_time,
                    EndTime=end_time,
                    Period=86400,
                    Statistics=["Average"]
                )
                
                avg_cpu = 0.0
                if cpu_metric["Datapoints"]:
                    avg_cpu = sum(dp["Average"] for dp in cpu_metric["Datapoints"]) / len(cpu_metric["Datapoints"])
                
                # Check memory utilization
                memory_metric = cloudwatch_client.get_metric_statistics(
                    Namespace="AWS/ECS",
                    MetricName="MemoryUtilization",
                    Dimensions=[
                        {"Name": "ServiceName", "Value": service_name},
                        {"Name": "ClusterName", "Value": cluster_name}
                    ],
                    StartTime=start_time,
                    EndTime=end_time,
                    Period=86400,
                    Statistics=["Average"]
                )
                
                avg_memory = 0.0
                if memory_metric["Datapoints"]:
                    avg_memory = sum(dp["Average"] for dp in memory_metric["Datapoints"]) / len(memory_metric["Datapoints"])
                
                if avg_cpu < 20 and avg_memory < 20:
                    service_arn = service["serviceArn"]
                    desired_count = service.get("desiredCount", 0)
                    running_count = service.get("runningCount", 0)
                    launch_type = service.get("launchType", "N/A")
                    
                    # Get tags
                    tags = {}
                    try:
                        tags_response = ecs_client.list_tags_for_resource(resourceArn=service_arn)
                        tags = {tag["key"]: tag["value"] for tag in tags_response.get("tags", [])}
                    except Exception:
                        pass
                    
                    output_data.append({
                        "ServiceName": service_name,
                        "ServiceArn": service_arn,
                        "ClusterName": cluster_name,
                        "LaunchType": launch_type,
                        "DesiredCount": desired_count,
                        "RunningCount": running_count,
                        "AverageCPUUtilization": f"{avg_cpu:.2f}%",
                        "AverageMemoryUtilization": f"{avg_memory:.2f}%",
                        "Tags": str(tags),
                        "Recommendation": "Consider reducing task count or task size",
                    })
        
        fields = {
            "1": "ServiceName",
            "2": "ClusterName",
            "3": "LaunchType",
            "4": "DesiredCount",
            "5": "RunningCount",
            "6": "AverageCPUUtilization",
            "7": "AverageMemoryUtilization",
            "8": "Recommendation",
            "9": "ServiceArn",
            "10": "Tags",
        }
        
        return {
            "id": 220,
            "name": "Underutilized ECS Services",
            "fields": fields,
            "headers": fields_to_headers(fields),
            "count": len(output_data),
            "resource": output_data,
        }
        
    except Exception as e:
        logger.error(f"Error finding underutilized ECS services: {e}")
        raise
