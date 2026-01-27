"""Compute upgrade recommendation tools for AWS resources."""

import logging
from datetime import datetime, timedelta
from typing import Any

from ..utils.helpers import fields_to_headers

logger = logging.getLogger(__name__)

# Deprecated Lambda runtimes (as of 2024)
DEPRECATED_RUNTIMES = {
    "python2.7": "2021-07-15",
    "python3.6": "2022-07-18",
    "python3.7": "2023-11-27",
    "nodejs10.x": "2021-07-30",
    "nodejs12.x": "2023-03-31",
    "nodejs14.x": "2023-11-27",
    "ruby2.5": "2021-07-30",
    "ruby2.7": "2023-12-07",
    "dotnetcore2.1": "2022-01-05",
    "dotnetcore3.1": "2023-04-03",
    "java8": "2024-01-08",
    "go1.x": "2023-12-31",
}

# Old generation EC2 instance types
OLD_GENERATION_TYPES = {
    "t2": "t3",
    "m4": "m5",
    "m5": "m6i",
    "c4": "c5",
    "c5": "c6i",
    "r4": "r5",
    "r5": "r6i",
    "i3": "i4i",
    "d2": "d3",
}


def find_outdated_lambda_runtimes(
    session: Any, region_name: str
) -> dict[str, Any]:
    """Find Lambda functions with deprecated or outdated runtimes.
    
    Args:
        session: Boto3 session
        region_name: AWS region name
    
    Returns:
        Dictionary with Lambda functions using outdated runtimes
    """
    lambda_client = session.client("lambda", region_name=region_name)
    
    output_data = []
    
    logger.info(f"Finding outdated Lambda runtimes in {region_name}")
    
    try:
        # Get all Lambda functions
        paginator = lambda_client.get_paginator("list_functions")
        
        for page in paginator.paginate():
            for function in page["Functions"]:
                function_name = function["FunctionName"]
                function_arn = function["FunctionArn"]
                runtime = function.get("Runtime", "N/A")
                
                # Check if runtime is deprecated
                is_deprecated = runtime in DEPRECATED_RUNTIMES
                
                if is_deprecated or runtime == "N/A":
                    # Get function details
                    memory_size = function.get("MemorySize", 0)
                    timeout = function.get("Timeout", 0)
                    code_size = function.get("CodeSize", 0)
                    last_modified = function.get("LastModified", "N/A")
                    
                    # Get tags
                    tags = {}
                    try:
                        tags_response = lambda_client.list_tags(Resource=function_arn)
                        tags = tags_response.get("Tags", {})
                    except Exception:
                        pass
                    
                    # Determine recommended runtime
                    recommended_runtime = "N/A"
                    if runtime.startswith("python"):
                        recommended_runtime = "python3.12"
                    elif runtime.startswith("nodejs"):
                        recommended_runtime = "nodejs20.x"
                    elif runtime.startswith("ruby"):
                        recommended_runtime = "ruby3.2"
                    elif runtime.startswith("dotnet"):
                        recommended_runtime = "dotnet8"
                    elif runtime.startswith("java"):
                        recommended_runtime = "java21"
                    elif runtime.startswith("go"):
                        recommended_runtime = "provided.al2023"
                    
                    deprecation_date = DEPRECATED_RUNTIMES.get(runtime, "Unknown")
                    
                    output_data.append({
                        "FunctionName": function_name,
                        "FunctionArn": function_arn,
                        "CurrentRuntime": runtime,
                        "RecommendedRuntime": recommended_runtime,
                        "DeprecationDate": deprecation_date,
                        "MemorySize": f"{memory_size} MB",
                        "Timeout": f"{timeout} seconds",
                        "CodeSize": f"{code_size / 1024:.2f} KB",
                        "LastModified": last_modified,
                        "Tags": str(tags),
                        "Recommendation": f"Upgrade from {runtime} to {recommended_runtime}",
                    })
        
        fields = {
            "1": "FunctionName",
            "2": "CurrentRuntime",
            "3": "RecommendedRuntime",
            "4": "DeprecationDate",
            "5": "MemorySize",
            "6": "Timeout",
            "7": "CodeSize",
            "8": "LastModified",
            "9": "Recommendation",
            "10": "FunctionArn",
            "11": "Tags",
        }
        
        return {
            "id": 403,
            "name": "Outdated Lambda Runtimes",
            "fields": fields,
            "headers": fields_to_headers(fields),
            "count": len(output_data),
            "resource": output_data,
        }
        
    except Exception as e:
        logger.error(f"Error finding outdated Lambda runtimes: {e}")
        raise


def find_ec2_instances_with_old_generations(
    session: Any, region_name: str
) -> dict[str, Any]:
    """Find EC2 instances using previous generation instance types.
    
    Args:
        session: Boto3 session
        region_name: AWS region name
    
    Returns:
        Dictionary with EC2 instances using old generation types
    """
    ec2_client = session.client("ec2", region_name=region_name)
    
    output_data = []
    
    logger.info(f"Finding EC2 instances with old generation types in {region_name}")
    
    try:
        # Get all running instances
        paginator = ec2_client.get_paginator("describe_instances")
        
        for page in paginator.paginate(Filters=[{"Name": "instance-state-name", "Values": ["running", "stopped"]}]):
            for reservation in page["Reservations"]:
                for instance in reservation["Instances"]:
                    instance_id = instance["InstanceId"]
                    instance_type = instance["InstanceType"]
                    instance_state = instance["State"]["Name"]
                    
                    # Extract instance family (e.g., "t2" from "t2.micro")
                    instance_family = instance_type.split(".")[0]
                    
                    # Check if it's an old generation
                    if instance_family in OLD_GENERATION_TYPES:
                        recommended_family = OLD_GENERATION_TYPES[instance_family]
                        instance_size = instance_type.split(".")[1] if "." in instance_type else "micro"
                        recommended_type = f"{recommended_family}.{instance_size}"
                        
                        # Get instance details
                        launch_time = instance.get("LaunchTime")
                        age_days = 0
                        if launch_time:
                            age_days = (datetime.now(launch_time.tzinfo) - launch_time).days
                        
                        platform = instance.get("Platform", "Linux")
                        vpc_id = instance.get("VpcId", "N/A")
                        subnet_id = instance.get("SubnetId", "N/A")
                        
                        # Get tags
                        tags = {tag["Key"]: tag["Value"] for tag in instance.get("Tags", [])}
                        name = tags.get("Name", "N/A")
                        
                        # Estimate cost savings (newer generations typically 10-20% cheaper)
                        # This is a rough estimate
                        estimated_savings_percentage = 15.0
                        
                        output_data.append({
                            "InstanceId": instance_id,
                            "InstanceName": name,
                            "CurrentInstanceType": instance_type,
                            "RecommendedInstanceType": recommended_type,
                            "InstanceState": instance_state,
                            "Platform": platform,
                            "AgeDays": age_days,
                            "VpcId": vpc_id,
                            "SubnetId": subnet_id,
                            "EstimatedSavingsPercentage": f"{estimated_savings_percentage}%",
                            "Tags": str(tags),
                            "Recommendation": f"Upgrade from {instance_type} to {recommended_type} for better performance and cost",
                        })
        
        fields = {
            "1": "InstanceId",
            "2": "InstanceName",
            "3": "CurrentInstanceType",
            "4": "RecommendedInstanceType",
            "5": "InstanceState",
            "6": "Platform",
            "7": "AgeDays",
            "8": "EstimatedSavingsPercentage",
            "9": "Recommendation",
            "10": "VpcId",
            "11": "Tags",
        }
        
        return {
            "id": 404,
            "name": "EC2 Instances with Old Generations",
            "fields": fields,
            "headers": fields_to_headers(fields),
            "count": len(output_data),
            "resource": output_data,
        }
        
    except Exception as e:
        logger.error(f"Error finding EC2 instances with old generations: {e}")
        raise


def find_ebs_volumes_with_old_types(
    session: Any, region_name: str
) -> dict[str, Any]:
    """Find EBS volumes using previous generation volume types.
    
    Args:
        session: Boto3 session
        region_name: AWS region name
    
    Returns:
        Dictionary with EBS volumes using old types
    """
    ec2_client = session.client("ec2", region_name=region_name)
    
    output_data = []
    
    logger.info(f"Finding EBS volumes with old types in {region_name}")
    
    try:
        # Get all volumes
        paginator = ec2_client.get_paginator("describe_volumes")
        
        # Old volume types that should be upgraded
        old_volume_types = {
            "standard": "gp3",  # Magnetic -> GP3
            "io1": "io2",       # IO1 -> IO2
            "gp2": "gp3",       # GP2 -> GP3
        }
        
        for page in paginator.paginate():
            for volume in page["Volumes"]:
                volume_id = volume["VolumeId"]
                volume_type = volume["VolumeType"]
                
                # Check if it's an old type
                if volume_type in old_volume_types:
                    recommended_type = old_volume_types[volume_type]
                    
                    size = volume["Size"]
                    state = volume["State"]
                    iops = volume.get("Iops", 0)
                    throughput = volume.get("Throughput", 0)
                    encrypted = volume.get("Encrypted", False)
                    
                    # Get attachment info
                    attachments = volume.get("Attachments", [])
                    attached_to = "N/A"
                    if attachments:
                        attached_to = attachments[0].get("InstanceId", "N/A")
                    
                    # Get tags
                    tags = {tag["Key"]: tag["Value"] for tag in volume.get("Tags", [])}
                    name = tags.get("Name", "N/A")
                    
                    # Calculate age
                    create_time = volume.get("CreateTime")
                    age_days = 0
                    if create_time:
                        age_days = (datetime.now(create_time.tzinfo) - create_time).days
                    
                    # Estimate cost savings
                    # GP3 is typically 20% cheaper than GP2
                    # IO2 is same price as IO1 but better durability
                    estimated_savings_percentage = 20.0 if volume_type in ["gp2", "standard"] else 0.0
                    estimated_monthly_cost = size * 0.10  # Rough estimate
                    estimated_monthly_savings = estimated_monthly_cost * (estimated_savings_percentage / 100)
                    
                    output_data.append({
                        "VolumeId": volume_id,
                        "VolumeName": name,
                        "CurrentVolumeType": volume_type,
                        "RecommendedVolumeType": recommended_type,
                        "Size": f"{size} GB",
                        "State": state,
                        "IOPS": iops,
                        "Throughput": f"{throughput} MB/s",
                        "Encrypted": "Yes" if encrypted else "No",
                        "AttachedTo": attached_to,
                        "AgeDays": age_days,
                        "EstimatedMonthlyCost": f"${estimated_monthly_cost:.2f}",
                        "EstimatedMonthlySavings": f"${estimated_monthly_savings:.2f}",
                        "EstimatedSavingsPercentage": f"{estimated_savings_percentage}%",
                        "Tags": str(tags),
                        "Recommendation": f"Upgrade from {volume_type} to {recommended_type}",
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
            "6": "State",
            "7": "IOPS",
            "8": "Encrypted",
            "9": "AttachedTo",
            "10": "EstimatedMonthlySavings",
            "11": "EstimatedSavingsPercentage",
            "12": "Recommendation",
            "13": "Tags",
        }
        
        return {
            "id": 405,
            "name": "EBS Volumes with Old Types",
            "fields": fields,
            "headers": fields_to_headers(fields),
            "count": len(output_data),
            "total_monthly_savings": f"${total_monthly_savings:.2f}",
            "resource": output_data,
        }
        
    except Exception as e:
        logger.error(f"Error finding EBS volumes with old types: {e}")
        raise


def find_outdated_ecs_platform_versions(
    session: Any, region_name: str
) -> dict[str, Any]:
    """Find ECS services not using the latest platform version.
    
    Args:
        session: Boto3 session
        region_name: AWS region name
    
    Returns:
        Dictionary with ECS services using outdated platform versions
    """
    ecs_client = session.client("ecs", region_name=region_name)
    
    output_data = []
    
    logger.info(f"Finding outdated ECS platform versions in {region_name}")
    
    try:
        # Get all clusters
        clusters_response = ecs_client.list_clusters()
        
        for cluster_arn in clusters_response.get("clusterArns", []):
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
                service_arn = service["serviceArn"]
                platform_version = service.get("platformVersion", "N/A")
                launch_type = service.get("launchType", "N/A")
                
                # Only check Fargate services (EC2 doesn't have platform versions)
                if launch_type != "FARGATE":
                    continue
                
                # Latest platform version is typically "LATEST" or "1.4.0"
                is_outdated = platform_version not in ["LATEST", "1.4.0"]
                
                if is_outdated:
                    desired_count = service.get("desiredCount", 0)
                    running_count = service.get("runningCount", 0)
                    status = service.get("status", "N/A")
                    
                    # Get task definition
                    task_definition_arn = service.get("taskDefinition", "N/A")
                    
                    # Get tags
                    tags = {}
                    try:
                        tags_response = ecs_client.list_tags_for_resource(resourceArn=service_arn)
                        tags = {tag["key"]: tag["value"] for tag in tags_response.get("tags", [])}
                    except Exception:
                        pass
                    
                    # Calculate age
                    created_at = service.get("createdAt")
                    age_days = 0
                    if created_at:
                        age_days = (datetime.now(created_at.tzinfo) - created_at).days
                    
                    output_data.append({
                        "ServiceName": service_name,
                        "ServiceArn": service_arn,
                        "ClusterArn": cluster_arn,
                        "CurrentPlatformVersion": platform_version,
                        "RecommendedPlatformVersion": "LATEST",
                        "LaunchType": launch_type,
                        "DesiredCount": desired_count,
                        "RunningCount": running_count,
                        "Status": status,
                        "TaskDefinition": task_definition_arn,
                        "AgeDays": age_days,
                        "Tags": str(tags),
                        "Recommendation": f"Update platform version from {platform_version} to LATEST",
                    })
        
        fields = {
            "1": "ServiceName",
            "2": "ClusterArn",
            "3": "CurrentPlatformVersion",
            "4": "RecommendedPlatformVersion",
            "5": "LaunchType",
            "6": "DesiredCount",
            "7": "RunningCount",
            "8": "Status",
            "9": "AgeDays",
            "10": "Recommendation",
            "11": "ServiceArn",
            "12": "Tags",
        }
        
        return {
            "id": 406,
            "name": "Outdated ECS Platform Versions",
            "fields": fields,
            "headers": fields_to_headers(fields),
            "count": len(output_data),
            "resource": output_data,
        }
        
    except Exception as e:
        logger.error(f"Error finding outdated ECS platform versions: {e}")
        raise
