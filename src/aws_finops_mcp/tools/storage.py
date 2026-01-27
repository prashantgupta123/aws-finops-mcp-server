"""Storage cleanup and optimization tools for AWS resources."""

import logging
from datetime import datetime, timedelta
from typing import Any

from ..utils.helpers import fields_to_headers

logger = logging.getLogger(__name__)


def find_unused_s3_buckets(
    session: Any, region_name: str = "us-east-1", period: int = 90
) -> dict[str, Any]:
    """Find S3 buckets with no GET/PUT requests in the specified period.
    
    Args:
        session: Boto3 session
        region_name: AWS region (S3 is global but metrics are regional)
        period: Lookback period in days
    
    Returns:
        Dictionary with unused S3 buckets
    """
    s3_client = session.client("s3")
    cloudwatch_client = session.client("cloudwatch", region_name="us-east-1")  # S3 metrics in us-east-1
    
    start_time = datetime.now() - timedelta(days=period)
    end_time = datetime.now()
    output_data = []
    
    logger.info("Finding unused S3 buckets")
    
    try:
        # Get all buckets
        response = s3_client.list_buckets()
        
        for bucket in response["Buckets"]:
            bucket_name = bucket["Name"]
            creation_date = bucket["CreationDate"]
            
            # Get bucket size and object count
            try:
                # Check CloudWatch metrics for requests
                has_activity = False
                for metric_name in ["NumberOfObjects", "BucketSizeBytes"]:
                    try:
                        metric_response = cloudwatch_client.get_metric_statistics(
                            Namespace="AWS/S3",
                            MetricName=metric_name,
                            Dimensions=[
                                {"Name": "BucketName", "Value": bucket_name},
                                {"Name": "StorageType", "Value": "AllStorageTypes"}
                            ],
                            StartTime=start_time,
                            EndTime=end_time,
                            Period=86400,
                            Statistics=["Average"],
                        )
                        
                        if metric_response["Datapoints"]:
                            has_activity = True
                            break
                    except Exception:
                        pass
                
                # Get bucket metrics for requests
                request_metrics = ["AllRequests", "GetRequests", "PutRequests"]
                has_requests = False
                
                for metric_name in request_metrics:
                    try:
                        metric_response = cloudwatch_client.get_metric_statistics(
                            Namespace="AWS/S3",
                            MetricName=metric_name,
                            Dimensions=[{"Name": "BucketName", "Value": bucket_name}],
                            StartTime=start_time,
                            EndTime=end_time,
                            Period=86400,
                            Statistics=["Sum"],
                        )
                        
                        if metric_response["Datapoints"]:
                            for datapoint in metric_response["Datapoints"]:
                                if datapoint.get("Sum", 0) > 0:
                                    has_requests = True
                                    break
                        
                        if has_requests:
                            break
                    except Exception:
                        pass
                
                # If no requests, consider it unused
                if not has_requests:
                    # Get bucket location
                    try:
                        location_response = s3_client.get_bucket_location(Bucket=bucket_name)
                        location = location_response.get("LocationConstraint") or "us-east-1"
                    except Exception:
                        location = "unknown"
                    
                    # Get bucket size (approximate)
                    try:
                        # Try to get object count
                        objects_response = s3_client.list_objects_v2(
                            Bucket=bucket_name,
                            MaxKeys=1
                        )
                        object_count = objects_response.get("KeyCount", 0)
                        
                        # Get bucket size from CloudWatch
                        size_response = cloudwatch_client.get_metric_statistics(
                            Namespace="AWS/S3",
                            MetricName="BucketSizeBytes",
                            Dimensions=[
                                {"Name": "BucketName", "Value": bucket_name},
                                {"Name": "StorageType", "Value": "StandardStorage"}
                            ],
                            StartTime=end_time - timedelta(days=1),
                            EndTime=end_time,
                            Period=86400,
                            Statistics=["Average"],
                        )
                        
                        bucket_size_bytes = 0
                        if size_response["Datapoints"]:
                            bucket_size_bytes = size_response["Datapoints"][0].get("Average", 0)
                        
                        bucket_size_gb = bucket_size_bytes / (1024 ** 3)
                    except Exception:
                        object_count = 0
                        bucket_size_gb = 0
                    
                    # Get versioning status
                    try:
                        versioning_response = s3_client.get_bucket_versioning(Bucket=bucket_name)
                        versioning_status = versioning_response.get("Status", "Disabled")
                    except Exception:
                        versioning_status = "Unknown"
                    
                    # Get storage class (default is STANDARD)
                    storage_class = "STANDARD"
                    
                    # Calculate estimated cost ($0.023/GB/month for Standard)
                    monthly_cost = bucket_size_gb * 0.023
                    
                    # Get tags
                    try:
                        tags_response = s3_client.get_bucket_tagging(Bucket=bucket_name)
                        tags = tags_response.get("TagSet", [])
                        tags_str = ", ".join([f"{tag['Key']}={tag['Value']}" for tag in tags]) if tags else "None"
                    except Exception:
                        tags_str = "None"
                    
                    # Calculate age
                    age_days = (datetime.now(creation_date.tzinfo) - creation_date).days
                    
                    output_data.append({
                        "BucketName": bucket_name,
                        "Region": location,
                        "CreationDate": creation_date.strftime("%Y-%m-%d %H:%M:%S"),
                        "AgeDays": age_days,
                        "NumberOfObjects": object_count,
                        "BucketSizeGB": f"{bucket_size_gb:.2f}",
                        "StorageClass": storage_class,
                        "VersioningStatus": versioning_status,
                        "EstimatedMonthlyCost": f"${monthly_cost:.2f}",
                        "Tags": tags_str,
                        "Description": f"S3 bucket with no requests in the last {period} days",
                    })
            
            except Exception as e:
                logger.debug(f"Error processing bucket {bucket_name}: {e}")
                continue
        
        # Calculate total potential savings
        total_monthly_cost = sum(
            float(bucket["EstimatedMonthlyCost"].replace("$", ""))
            for bucket in output_data
        )
        
        fields = {
            "1": "BucketName",
            "2": "Region",
            "3": "CreationDate",
            "4": "AgeDays",
            "5": "NumberOfObjects",
            "6": "BucketSizeGB",
            "7": "StorageClass",
            "8": "VersioningStatus",
            "9": "EstimatedMonthlyCost",
            "10": "Tags",
            "11": "Description",
        }
        
        return {
            "id": 204,
            "name": "Unused S3 Buckets",
            "fields": fields,
            "headers": fields_to_headers(fields),
            "count": len(output_data),
            "total_monthly_cost": f"${total_monthly_cost:.2f}",
            "resource": output_data,
        }
        
    except Exception as e:
        logger.error(f"Error finding unused S3 buckets: {e}")
        raise


def get_s3_storage_class_recommendations(
    session: Any, region_name: str = "us-east-1", min_size_gb: float = 1.0
) -> dict[str, Any]:
    """Get S3 storage class optimization recommendations.
    
    Args:
        session: Boto3 session
        region_name: AWS region
        min_size_gb: Minimum bucket size to analyze (GB)
    
    Returns:
        Dictionary with storage class recommendations
    """
    s3_client = session.client("s3")
    cloudwatch_client = session.client("cloudwatch", region_name="us-east-1")
    
    output_data = []
    
    logger.info("Analyzing S3 storage class optimization opportunities")
    
    try:
        # Get all buckets
        response = s3_client.list_buckets()
        
        for bucket in response["Buckets"]:
            bucket_name = bucket["Name"]
            
            try:
                # Get bucket size
                end_time = datetime.now()
                start_time = end_time - timedelta(days=1)
                
                size_response = cloudwatch_client.get_metric_statistics(
                    Namespace="AWS/S3",
                    MetricName="BucketSizeBytes",
                    Dimensions=[
                        {"Name": "BucketName", "Value": bucket_name},
                        {"Name": "StorageType", "Value": "StandardStorage"}
                    ],
                    StartTime=start_time,
                    EndTime=end_time,
                    Period=86400,
                    Statistics=["Average"],
                )
                
                bucket_size_bytes = 0
                if size_response["Datapoints"]:
                    bucket_size_bytes = size_response["Datapoints"][0].get("Average", 0)
                
                bucket_size_gb = bucket_size_bytes / (1024 ** 3)
                
                # Skip small buckets
                if bucket_size_gb < min_size_gb:
                    continue
                
                # Get object count
                count_response = cloudwatch_client.get_metric_statistics(
                    Namespace="AWS/S3",
                    MetricName="NumberOfObjects",
                    Dimensions=[
                        {"Name": "BucketName", "Value": bucket_name},
                        {"Name": "StorageType", "Value": "AllStorageTypes"}
                    ],
                    StartTime=start_time,
                    EndTime=end_time,
                    Period=86400,
                    Statistics=["Average"],
                )
                
                object_count = 0
                if count_response["Datapoints"]:
                    object_count = int(count_response["Datapoints"][0].get("Average", 0))
                
                # Check if Intelligent-Tiering is enabled
                try:
                    lifecycle_response = s3_client.get_bucket_lifecycle_configuration(Bucket=bucket_name)
                    has_lifecycle = True
                    has_intelligent_tiering = any(
                        rule.get("Transitions", [{}])[0].get("StorageClass") == "INTELLIGENT_TIERING"
                        for rule in lifecycle_response.get("Rules", [])
                        if rule.get("Transitions")
                    )
                except Exception:
                    has_lifecycle = False
                    has_intelligent_tiering = False
                
                # Recommend Intelligent-Tiering if not already enabled
                if not has_intelligent_tiering and bucket_size_gb > 10:
                    current_cost = bucket_size_gb * 0.023  # Standard storage
                    recommended_cost = bucket_size_gb * 0.023  # Same base, but auto-tiering saves on infrequent access
                    estimated_savings = current_cost * 0.30  # Assume 30% savings on average
                    
                    output_data.append({
                        "BucketName": bucket_name,
                        "CurrentStorageClass": "STANDARD",
                        "RecommendedStorageClass": "INTELLIGENT_TIERING",
                        "ObjectCount": object_count,
                        "TotalSizeGB": f"{bucket_size_gb:.2f}",
                        "CurrentMonthlyCost": f"${current_cost:.2f}",
                        "EstimatedMonthlySavings": f"${estimated_savings:.2f}",
                        "SavingsPercentage": "30%",
                        "Recommendation": "Enable S3 Intelligent-Tiering for automatic cost optimization",
                    })
            
            except Exception as e:
                logger.debug(f"Error analyzing bucket {bucket_name}: {e}")
                continue
        
        # Calculate total potential savings
        total_monthly_savings = sum(
            float(rec["EstimatedMonthlySavings"].replace("$", ""))
            for rec in output_data
        )
        
        fields = {
            "1": "BucketName",
            "2": "CurrentStorageClass",
            "3": "RecommendedStorageClass",
            "4": "ObjectCount",
            "5": "TotalSizeGB",
            "6": "CurrentMonthlyCost",
            "7": "EstimatedMonthlySavings",
            "8": "SavingsPercentage",
            "9": "Recommendation",
        }
        
        return {
            "id": 301,
            "name": "S3 Storage Class Recommendations",
            "fields": fields,
            "headers": fields_to_headers(fields),
            "count": len(output_data),
            "total_monthly_savings": f"${total_monthly_savings:.2f}",
            "resource": output_data,
        }
        
    except Exception as e:
        logger.error(f"Error getting S3 storage class recommendations: {e}")
        raise
