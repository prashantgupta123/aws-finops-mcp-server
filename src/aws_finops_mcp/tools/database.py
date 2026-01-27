"""Database cleanup and optimization tools for AWS resources."""

import logging
from datetime import datetime, timedelta
from typing import Any

from ..utils.helpers import fields_to_headers

logger = logging.getLogger(__name__)


def find_unused_dynamodb_tables(
    session: Any, region_name: str, period: int = 90
) -> dict[str, Any]:
    """Find DynamoDB tables with no read/write activity in the specified period.
    
    Args:
        session: Boto3 session
        region_name: AWS region name
        period: Lookback period in days
    
    Returns:
        Dictionary with unused DynamoDB tables
    """
    dynamodb_client = session.client("dynamodb", region_name=region_name)
    cloudwatch_client = session.client("cloudwatch", region_name=region_name)
    
    start_time = datetime.now() - timedelta(days=period)
    end_time = datetime.now()
    output_data = []
    
    logger.info(f"Finding unused DynamoDB tables in {region_name}")
    
    try:
        # Get all tables
        tables_response = dynamodb_client.list_tables()
        
        for table_name in tables_response.get("TableNames", []):
            try:
                # Get table details
                table_response = dynamodb_client.describe_table(TableName=table_name)
                table = table_response["Table"]
                
                # Check CloudWatch metrics for activity
                has_activity = False
                for metric_name in ["ConsumedReadCapacityUnits", "ConsumedWriteCapacityUnits"]:
                    try:
                        metric_response = cloudwatch_client.get_metric_statistics(
                            Namespace="AWS/DynamoDB",
                            MetricName=metric_name,
                            Dimensions=[{"Name": "TableName", "Value": table_name}],
                            StartTime=start_time,
                            EndTime=end_time,
                            Period=86400,
                            Statistics=["Sum"],
                        )
                        
                        if metric_response["Datapoints"]:
                            for datapoint in metric_response["Datapoints"]:
                                if datapoint.get("Sum", 0) > 0:
                                    has_activity = True
                                    break
                        
                        if has_activity:
                            break
                    except Exception:
                        pass
                
                if not has_activity:
                    table_status = table.get("TableStatus", "ACTIVE")
                    item_count = table.get("ItemCount", 0)
                    table_size_bytes = table.get("TableSizeBytes", 0)
                    table_size_gb = table_size_bytes / (1024 ** 3)
                    billing_mode = table.get("BillingModeSummary", {}).get("BillingMode", "PROVISIONED")
                    
                    # Get provisioned capacity
                    read_capacity = 0
                    write_capacity = 0
                    if billing_mode == "PROVISIONED":
                        provisioned_throughput = table.get("ProvisionedThroughput", {})
                        read_capacity = provisioned_throughput.get("ReadCapacityUnits", 0)
                        write_capacity = provisioned_throughput.get("WriteCapacityUnits", 0)
                    
                    # Calculate estimated cost
                    monthly_cost = 0
                    if billing_mode == "PROVISIONED":
                        # $0.00065/hour per RCU, $0.00065/hour per WCU
                        monthly_cost = (read_capacity + write_capacity) * 0.00065 * 24 * 30
                    # Storage: $0.25/GB/month
                    monthly_cost += table_size_gb * 0.25
                    
                    # Get tags
                    try:
                        tags_response = dynamodb_client.list_tags_of_resource(
                            ResourceArn=table["TableArn"]
                        )
                        tags = tags_response.get("Tags", [])
                        tags_str = ", ".join([f"{tag['Key']}={tag['Value']}" for tag in tags]) if tags else "None"
                    except Exception:
                        tags_str = "None"
                    
                    # Get creation time
                    creation_time = table.get("CreationDateTime")
                    age_days = 0
                    if creation_time:
                        age_days = (datetime.now(creation_time.tzinfo) - creation_time).days
                    
                    output_data.append({
                        "TableName": table_name,
                        "TableStatus": table_status,
                        "ItemCount": item_count,
                        "TableSizeGB": f"{table_size_gb:.2f}",
                        "BillingMode": billing_mode,
                        "ReadCapacityUnits": read_capacity,
                        "WriteCapacityUnits": write_capacity,
                        "CreationTime": creation_time.strftime("%Y-%m-%d %H:%M:%S") if creation_time else "N/A",
                        "AgeDays": age_days,
                        "EstimatedMonthlyCost": f"${monthly_cost:.2f}",
                        "Tags": tags_str,
                        "Description": f"DynamoDB table with no activity in the last {period} days",
                    })
            
            except Exception as e:
                logger.debug(f"Error processing table {table_name}: {e}")
                continue
        
        # Calculate total potential savings
        total_monthly_cost = sum(
            float(table["EstimatedMonthlyCost"].replace("$", ""))
            for table in output_data
        )
        
        fields = {
            "1": "TableName",
            "2": "TableStatus",
            "3": "ItemCount",
            "4": "TableSizeGB",
            "5": "BillingMode",
            "6": "ReadCapacityUnits",
            "7": "WriteCapacityUnits",
            "8": "CreationTime",
            "9": "AgeDays",
            "10": "EstimatedMonthlyCost",
            "11": "Tags",
            "12": "Description",
        }
        
        return {
            "id": 213,
            "name": "Unused DynamoDB Tables",
            "fields": fields,
            "headers": fields_to_headers(fields),
            "count": len(output_data),
            "total_monthly_cost": f"${total_monthly_cost:.2f}",
            "resource": output_data,
        }
        
    except Exception as e:
        logger.error(f"Error finding unused DynamoDB tables: {e}")
        raise


def find_underutilized_dynamodb_tables(
    session: Any, region_name: str, period: int = 30
) -> dict[str, Any]:
    """Find DynamoDB tables with low capacity utilization.
    
    Args:
        session: Boto3 session
        region_name: AWS region name
        period: Lookback period in days
    
    Returns:
        Dictionary with underutilized DynamoDB tables
    """
    dynamodb_client = session.client("dynamodb", region_name=region_name)
    cloudwatch_client = session.client("cloudwatch", region_name=region_name)
    
    start_time = datetime.now() - timedelta(days=period)
    end_time = datetime.now()
    output_data = []
    
    logger.info(f"Finding underutilized DynamoDB tables in {region_name}")
    
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
                
                provisioned_throughput = table.get("ProvisionedThroughput", {})
                provisioned_read = provisioned_throughput.get("ReadCapacityUnits", 0)
                provisioned_write = provisioned_throughput.get("WriteCapacityUnits", 0)
                
                if provisioned_read == 0 and provisioned_write == 0:
                    continue
                
                # Get consumed capacity from CloudWatch
                consumed_read = 0
                consumed_write = 0
                
                for metric_name, consumed_var in [
                    ("ConsumedReadCapacityUnits", "consumed_read"),
                    ("ConsumedWriteCapacityUnits", "consumed_write")
                ]:
                    try:
                        metric_response = cloudwatch_client.get_metric_statistics(
                            Namespace="AWS/DynamoDB",
                            MetricName=metric_name,
                            Dimensions=[{"Name": "TableName", "Value": table_name}],
                            StartTime=start_time,
                            EndTime=end_time,
                            Period=86400,
                            Statistics=["Average"],
                        )
                        
                        if metric_response["Datapoints"]:
                            avg_consumed = sum(dp.get("Average", 0) for dp in metric_response["Datapoints"]) / len(metric_response["Datapoints"])
                            if metric_name == "ConsumedReadCapacityUnits":
                                consumed_read = avg_consumed
                            else:
                                consumed_write = avg_consumed
                    except Exception:
                        pass
                
                # Calculate utilization
                read_utilization = (consumed_read / provisioned_read * 100) if provisioned_read > 0 else 0
                write_utilization = (consumed_write / provisioned_write * 100) if provisioned_write > 0 else 0
                avg_utilization = (read_utilization + write_utilization) / 2
                
                # Flag if utilization < 20%
                if avg_utilization < 20:
                    # Calculate potential savings
                    current_cost = (provisioned_read + provisioned_write) * 0.00065 * 24 * 30
                    
                    # Recommend on-demand or lower capacity
                    recommended_action = "Switch to on-demand billing"
                    if consumed_read > 0 or consumed_write > 0:
                        recommended_read = max(1, int(consumed_read * 1.2))
                        recommended_write = max(1, int(consumed_write * 1.2))
                        recommended_cost = (recommended_read + recommended_write) * 0.00065 * 24 * 30
                        estimated_savings = current_cost - recommended_cost
                        recommended_action = f"Reduce to {recommended_read} RCU / {recommended_write} WCU"
                    else:
                        estimated_savings = current_cost * 0.8
                    
                    output_data.append({
                        "TableName": table_name,
                        "BillingMode": billing_mode,
                        "ProvisionedReadCapacity": provisioned_read,
                        "ProvisionedWriteCapacity": provisioned_write,
                        "ConsumedReadCapacity": f"{consumed_read:.2f}",
                        "ConsumedWriteCapacity": f"{consumed_write:.2f}",
                        "ReadUtilizationPercent": f"{read_utilization:.1f}%",
                        "WriteUtilizationPercent": f"{write_utilization:.1f}%",
                        "AvgUtilizationPercent": f"{avg_utilization:.1f}%",
                        "RecommendedAction": recommended_action,
                        "EstimatedMonthlySavings": f"${estimated_savings:.2f}",
                    })
            
            except Exception as e:
                logger.debug(f"Error processing table {table_name}: {e}")
                continue
        
        # Calculate total potential savings
        total_monthly_savings = sum(
            float(table["EstimatedMonthlySavings"].replace("$", ""))
            for table in output_data
        )
        
        fields = {
            "1": "TableName",
            "2": "BillingMode",
            "3": "ProvisionedReadCapacity",
            "4": "ProvisionedWriteCapacity",
            "5": "ConsumedReadCapacity",
            "6": "ConsumedWriteCapacity",
            "7": "ReadUtilizationPercent",
            "8": "WriteUtilizationPercent",
            "9": "AvgUtilizationPercent",
            "10": "RecommendedAction",
            "11": "EstimatedMonthlySavings",
        }
        
        return {
            "id": 214,
            "name": "Underutilized DynamoDB Tables",
            "fields": fields,
            "headers": fields_to_headers(fields),
            "count": len(output_data),
            "total_monthly_savings": f"${total_monthly_savings:.2f}",
            "resource": output_data,
        }
        
    except Exception as e:
        logger.error(f"Error finding underutilized DynamoDB tables: {e}")
        raise
