"""Storage cost optimization tools for AWS resources."""

import logging
from datetime import datetime, timedelta
from typing import Any

from ..utils.helpers import fields_to_headers

logger = logging.getLogger(__name__)


def get_ebs_volume_type_recommendations(
    session: Any, region_name: str
) -> dict[str, Any]:
    """Get recommendations for optimizing EBS volume types based on usage patterns.
    
    Args:
        session: Boto3 session
        region_name: AWS region name
    
    Returns:
        Dictionary with EBS volume type recommendations
    """
    ec2_client = session.client("ec2", region_name=region_name)
    cloudwatch_client = session.client("cloudwatch", region_name=region_name)
    
    output_data = []
    
    logger.info(f"Getting EBS volume type recommendations in {region_name}")
    
    try:
        # Get all volumes
        paginator = ec2_client.get_paginator("describe_volumes")
        
        start_time = datetime.now() - timedelta(days=14)
        end_time = datetime.now()
        
        for page in paginator.paginate():
            for volume in page["Volumes"]:
                volume_id = volume["VolumeId"]
                volume_type = volume["VolumeType"]
                size = volume["Size"]
                iops = volume.get("Iops", 0)
                throughput = volume.get("Throughput", 0)
                
                # Check IOPS usage
                read_ops_metric = cloudwatch_client.get_metric_statistics(
                    Namespace="AWS/EBS",
                    MetricName="VolumeReadOps",
                    Dimensions=[{"Name": "VolumeId", "Value": volume_id}],
                    StartTime=start_time,
                    EndTime=end_time,
                    Period=86400,
                    Statistics=["Average"]
                )
                
                write_ops_metric = cloudwatch_client.get_metric_statistics(
                    Namespace="AWS/EBS",
                    MetricName="VolumeWriteOps",
                    Dimensions=[{"Name": "VolumeId", "Value": volume_id}],
                    StartTime=start_time,
                    EndTime=end_time,
                    Period=86400,
                    Statistics=["Average"]
                )
                
                avg_read_ops = 0
                avg_write_ops = 0
                
                if read_ops_metric["Datapoints"]:
                    avg_read_ops = sum(dp["Average"] for dp in read_ops_metric["Datapoints"]) / len(read_ops_metric["Datapoints"])
                
                if write_ops_metric["Datapoints"]:
                    avg_write_ops = sum(dp["Average"] for dp in write_ops_metric["Datapoints"]) / len(write_ops_metric["Datapoints"])
                
                total_ops_per_second = (avg_read_ops + avg_write_ops) / 60  # Convert to per second
                
                # Determine recommended volume type
                recommended_type = volume_type
                estimated_savings = 0.0
                current_cost = 0.0
                recommended_cost = 0.0
                
                if volume_type == "gp2":
                    # GP2 pricing: $0.10/GB-month
                    current_cost = size * 0.10
                    # GP3 pricing: $0.08/GB-month + $0.005/provisioned IOPS + $0.04/MB/s throughput
                    recommended_type = "gp3"
                    recommended_cost = size * 0.08
                    estimated_savings = current_cost - recommended_cost
                elif volume_type == "io1" and total_ops_per_second < 16000:
                    # IO1 pricing: $0.125/GB-month + $0.065/provisioned IOPS
                    current_cost = size * 0.125 + iops * 0.065
                    # IO2 pricing: $0.125/GB-month + $0.065/provisioned IOPS (same price, better durability)
                    recommended_type = "io2"
                    recommended_cost = current_cost
                    estimated_savings = 0
                elif volume_type == "standard":
                    # Magnetic pricing: $0.05/GB-month + $0.05/million I/O requests
                    current_cost = size * 0.05
                    recommended_type = "gp3"
                    recommended_cost = size * 0.08
                    estimated_savings = current_cost - recommended_cost
                
                if recommended_type != volume_type or estimated_savings > 0:
                    # Get tags
                    tags = {tag["Key"]: tag["Value"] for tag in volume.get("Tags", [])}
                    name = tags.get("Name", "N/A")
                    
                    # Get attachment info
                    attachments = volume.get("Attachments", [])
                    attached_to = "N/A"
                    if attachments:
                        attached_to = attachments[0].get("InstanceId", "N/A")
                    
                    output_data.append({
                        "VolumeId": volume_id,
                        "VolumeName": name,
                        "CurrentVolumeType": volume_type,
                        "RecommendedVolumeType": recommended_type,
                        "Size": f"{size} GB",
                        "CurrentIOPS": iops,
                        "AverageIOPS": f"{total_ops_per_second:.2f}",
                        "CurrentMonthlyCost": f"${current_cost:.2f}",
                        "RecommendedMonthlyCost": f"${recommended_cost:.2f}",
                        "EstimatedMonthlySavings": f"${estimated_savings:.2f}",
                        "AttachedTo": attached_to,
                        "Tags": str(tags),
                        "Recommendation": f"Change from {volume_type} to {recommended_type}",
                    })
        
        total_monthly_savings = sum(
            float(item["EstimatedMonthlySavings"].replace("$", ""))
            for item in output_data
        )
        
        fields = {
            "1": "VolumeId",
            "2": "VolumeName",
            "3": "CurrentVolumeType",
            "4": "RecommendedVolumeType",
            "5": "Size",
            "6": "AverageIOPS",
            "7": "CurrentMonthlyCost",
            "8": "RecommendedMonthlyCost",
            "9": "EstimatedMonthlySavings",
            "10": "Recommendation",
            "11": "Tags",
        }
        
        return {
            "id": 305,
            "name": "EBS Volume Type Recommendations",
            "fields": fields,
            "headers": fields_to_headers(fields),
            "count": len(output_data),
            "total_monthly_savings": f"${total_monthly_savings:.2f}",
            "resource": output_data,
        }
        
    except Exception as e:
        logger.error(f"Error getting EBS volume type recommendations: {e}")
        raise


def get_snapshot_lifecycle_recommendations(
    session: Any, region_name: str, retention_days: int = 30
) -> dict[str, Any]:
    """Get recommendations for snapshot lifecycle management and cleanup.
    
    Args:
        session: Boto3 session
        region_name: AWS region name
        retention_days: Recommended retention period in days
    
    Returns:
        Dictionary with snapshot lifecycle recommendations
    """
    ec2_client = session.client("ec2", region_name=region_name)
    
    output_data = []
    
    logger.info(f"Getting snapshot lifecycle recommendations in {region_name}")
    
    try:
        # Get all snapshots owned by the account
        paginator = ec2_client.get_paginator("describe_snapshots")
        
        for page in paginator.paginate(OwnerIds=["self"]):
            for snapshot in page["Snapshots"]:
                snapshot_id = snapshot["SnapshotId"]
                volume_id = snapshot.get("VolumeId", "N/A")
                start_time = snapshot["StartTime"]
                volume_size = snapshot["VolumeSize"]
                state = snapshot["State"]
                
                # Calculate age
                age_days = (datetime.now(start_time.tzinfo) - start_time).days
                
                # Check if volume still exists
                volume_exists = False
                if volume_id != "N/A":
                    try:
                        ec2_client.describe_volumes(VolumeIds=[volume_id])
                        volume_exists = True
                    except Exception:
                        volume_exists = False
                
                # Determine recommendation
                recommendation = ""
                should_delete = False
                
                if age_days > retention_days and not volume_exists:
                    recommendation = f"Delete snapshot (>{retention_days} days old, volume deleted)"
                    should_delete = True
                elif age_days > retention_days * 2:
                    recommendation = f"Consider deleting snapshot (>{retention_days * 2} days old)"
                    should_delete = True
                elif not volume_exists:
                    recommendation = "Volume deleted - review if snapshot still needed"
                
                if recommendation:
                    # Get tags
                    tags = {tag["Key"]: tag["Value"] for tag in snapshot.get("Tags", [])}
                    description = snapshot.get("Description", "N/A")
                    
                    # Estimate cost ($0.05 per GB-month)
                    estimated_monthly_cost = volume_size * 0.05
                    
                    output_data.append({
                        "SnapshotId": snapshot_id,
                        "VolumeId": volume_id,
                        "VolumeExists": "Yes" if volume_exists else "No",
                        "Size": f"{volume_size} GB",
                        "State": state,
                        "AgeDays": age_days,
                        "StartTime": start_time.strftime("%Y-%m-%d"),
                        "Description": description,
                        "EstimatedMonthlyCost": f"${estimated_monthly_cost:.2f}",
                        "ShouldDelete": "Yes" if should_delete else "Review",
                        "Tags": str(tags),
                        "Recommendation": recommendation,
                    })
        
        total_monthly_cost = sum(
            float(item["EstimatedMonthlyCost"].replace("$", ""))
            for item in output_data
        )
        
        fields = {
            "1": "SnapshotId",
            "2": "VolumeId",
            "3": "VolumeExists",
            "4": "Size",
            "5": "AgeDays",
            "6": "StartTime",
            "7": "EstimatedMonthlyCost",
            "8": "ShouldDelete",
            "9": "Recommendation",
            "10": "Tags",
        }
        
        return {
            "id": 306,
            "name": "Snapshot Lifecycle Recommendations",
            "fields": fields,
            "headers": fields_to_headers(fields),
            "count": len(output_data),
            "total_monthly_cost": f"${total_monthly_cost:.2f}",
            "resource": output_data,
        }
        
    except Exception as e:
        logger.error(f"Error getting snapshot lifecycle recommendations: {e}")
        raise
