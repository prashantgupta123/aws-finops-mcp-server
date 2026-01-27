"""Capacity analysis tools for EC2 and RDS instances."""

import logging
from datetime import datetime, timedelta
from typing import Any

from ..utils.helpers import fields_to_headers, safe_float
from ..utils.metrics import calculate_metrics, get_metric_statistics

logger = logging.getLogger(__name__)


def find_underutilized_ec2_instances(
    session: Any, region_name: str, period: int, max_results: int = 100
) -> dict[str, Any]:
    """Find EC2 instances with low CPU and memory utilization."""
    ec2_client = session.client("ec2", region_name=region_name)
    cloudwatch_client = session.client("cloudwatch", region_name=region_name)
    
    start_time = datetime.now() - timedelta(days=period)
    end_time = datetime.now()
    
    # Get running instances
    response = ec2_client.describe_instances(
        Filters=[{"Name": "instance-state-name", "Values": ["running"]}],
        MaxResults=max_results,
    )
    
    underutilized_instances = []
    
    for reservation in response["Reservations"]:
        for instance in reservation["Instances"]:
            instance_id = instance["InstanceId"]
            instance_type = instance["InstanceType"]
            
            # Get instance name and neglect tag
            instance_name = ""
            neglect = "False"
            for tag in instance.get("Tags", []):
                if tag["Key"] == "Name":
                    instance_name = tag["Value"]
                elif tag["Key"] == "Neglect":
                    neglect = tag["Value"]
            
            if not instance_name:
                continue
            
            # Get CPU metrics
            cpu_datapoints = get_metric_statistics(
                cloudwatch_client,
                "AWS/EC2",
                "CPUUtilization",
                [{"Name": "InstanceId", "Value": instance_id}],
                start_time,
                end_time,
            )
            
            # Get memory metrics (requires CloudWatch agent)
            memory_datapoints = get_metric_statistics(
                cloudwatch_client,
                "CWAgent",
                "mem_used_percent",
                [{"Name": "InstanceId", "Value": instance_id}],
                start_time,
                end_time,
            )
            
            cpu_avg, cpu_min, cpu_max = calculate_metrics(cpu_datapoints)
            memory_avg, memory_min, memory_max = calculate_metrics(memory_datapoints)
            
            # Check if underutilized (max CPU <= 20% AND max memory <= 20%)
            cpu_max_val = safe_float(cpu_max)
            memory_max_val = safe_float(memory_max)
            
            if cpu_max_val <= 20.0 and memory_max_val <= 20.0 and neglect == "False":
                cpu_options = instance.get("CpuOptions", {})
                vcpu = cpu_options.get("CoreCount", 1) * cpu_options.get("ThreadsPerCore", 1)
                
                memory_info = instance.get("MemoryInfo", {})
                memory_gib = memory_info.get("SizeInMiB", 1024) / 1024 if memory_info else 1
                
                underutilized_instances.append({
                    "InstanceId": instance_id,
                    "InstanceName": instance_name,
                    "InstanceType": instance_type,
                    "VpcId": instance.get("VpcId", ""),
                    "AvailabilityZone": instance.get("Placement", {}).get("AvailabilityZone", ""),
                    "Vcpu": vcpu,
                    "MemoryGiB": f"{memory_gib:.1f}",
                    "AvgCPUUtilization": safe_float(cpu_avg),
                    "MaxCPUUtilization": cpu_max_val,
                    "MaxMemoryUtilization": memory_max_val,
                    "Description": "Instance is underutilized. Consider downsizing to save costs.",
                })
    
    fields = {
        "1": "InstanceId",
        "2": "InstanceName",
        "3": "InstanceType",
        "4": "VpcId",
        "5": "AvailabilityZone",
        "6": "Vcpu",
        "7": "MemoryGiB",
        "8": "AvgCPUUtilization",
        "9": "MaxCPUUtilization",
        "10": "MaxMemoryUtilization",
        "11": "Description",
    }
    
    return {
        "id": 109,
        "name": "Underutilized EC2 Instances",
        "fields": fields,
        "headers": fields_to_headers(fields),
        "count": len(underutilized_instances),
        "resource": underutilized_instances,
    }


def find_overutilized_ec2_instances(
    session: Any, region_name: str, period: int, max_results: int = 100
) -> dict[str, Any]:
    """Find EC2 instances with high CPU or memory utilization."""
    ec2_client = session.client("ec2", region_name=region_name)
    cloudwatch_client = session.client("cloudwatch", region_name=region_name)
    
    start_time = datetime.now() - timedelta(days=period)
    end_time = datetime.now()
    
    # Get running instances
    response = ec2_client.describe_instances(
        Filters=[{"Name": "instance-state-name", "Values": ["running"]}],
        MaxResults=max_results,
    )
    
    overutilized_instances = []
    
    for reservation in response["Reservations"]:
        for instance in reservation["Instances"]:
            instance_id = instance["InstanceId"]
            instance_type = instance["InstanceType"]
            
            # Get instance name
            instance_name = ""
            for tag in instance.get("Tags", []):
                if tag["Key"] == "Name":
                    instance_name = tag["Value"]
            
            if not instance_name:
                continue
            
            # Get CPU metrics
            cpu_datapoints = get_metric_statistics(
                cloudwatch_client,
                "AWS/EC2",
                "CPUUtilization",
                [{"Name": "InstanceId", "Value": instance_id}],
                start_time,
                end_time,
            )
            
            # Get memory metrics
            memory_datapoints = get_metric_statistics(
                cloudwatch_client,
                "CWAgent",
                "mem_used_percent",
                [{"Name": "InstanceId", "Value": instance_id}],
                start_time,
                end_time,
            )
            
            cpu_avg, cpu_min, cpu_max = calculate_metrics(cpu_datapoints)
            memory_avg, memory_min, memory_max = calculate_metrics(memory_datapoints)
            
            # Check if overutilized (max CPU >= 80% OR max memory >= 80%)
            cpu_max_val = safe_float(cpu_max)
            memory_max_val = safe_float(memory_max)
            
            if cpu_max_val >= 80.0 or memory_max_val >= 80.0:
                cpu_options = instance.get("CpuOptions", {})
                vcpu = cpu_options.get("CoreCount", 1) * cpu_options.get("ThreadsPerCore", 1)
                
                memory_info = instance.get("MemoryInfo", {})
                memory_gib = memory_info.get("SizeInMiB", 1024) / 1024 if memory_info else 1
                
                overutilized_instances.append({
                    "InstanceId": instance_id,
                    "InstanceName": instance_name,
                    "InstanceType": instance_type,
                    "VpcId": instance.get("VpcId", ""),
                    "AvailabilityZone": instance.get("Placement", {}).get("AvailabilityZone", ""),
                    "Vcpu": vcpu,
                    "MemoryGiB": f"{memory_gib:.1f}",
                    "AvgCPUUtilization": safe_float(cpu_avg),
                    "MaxCPUUtilization": cpu_max_val,
                    "MaxMemoryUtilization": memory_max_val,
                    "Description": "Instance is overutilized. Consider upsizing for better performance.",
                })
    
    fields = {
        "1": "InstanceId",
        "2": "InstanceName",
        "3": "InstanceType",
        "4": "VpcId",
        "5": "AvailabilityZone",
        "6": "Vcpu",
        "7": "MemoryGiB",
        "8": "AvgCPUUtilization",
        "9": "MaxCPUUtilization",
        "10": "MaxMemoryUtilization",
        "11": "Description",
    }
    
    return {
        "id": 111,
        "name": "Overutilized EC2 Instances",
        "fields": fields,
        "headers": fields_to_headers(fields),
        "count": len(overutilized_instances),
        "resource": overutilized_instances,
    }


def find_underutilized_rds_instances(
    session: Any, region_name: str, period: int, max_results: int = 100
) -> dict[str, Any]:
    """Find RDS instances with low CPU utilization."""
    rds_client = session.client("rds", region_name=region_name)
    cloudwatch_client = session.client("cloudwatch", region_name=region_name)
    
    start_time = datetime.now() - timedelta(days=period)
    end_time = datetime.now()
    
    # Get all RDS instances
    response = rds_client.describe_db_instances(MaxRecords=max_results)
    underutilized_instances = []
    
    for db_instance in response["DBInstances"]:
        db_instance_id = db_instance["DBInstanceIdentifier"]
        db_instance_class = db_instance["DBInstanceClass"]
        
        # Get CPU metrics
        cpu_datapoints = get_metric_statistics(
            cloudwatch_client,
            "AWS/RDS",
            "CPUUtilization",
            [{"Name": "DBInstanceIdentifier", "Value": db_instance_id}],
            start_time,
            end_time,
        )
        
        cpu_avg, cpu_min, cpu_max = calculate_metrics(cpu_datapoints)
        cpu_max_val = safe_float(cpu_max)
        
        # Check if underutilized (max CPU <= 20%)
        if cpu_max_val <= 20.0:
            underutilized_instances.append({
                "InstanceName": db_instance_id,
                "InstanceType": db_instance_class,
                "Engine": db_instance.get("Engine", ""),
                "EngineVersion": db_instance.get("EngineVersion", ""),
                "AvailabilityZone": db_instance.get("AvailabilityZone", ""),
                "MultiAZ": db_instance.get("MultiAZ", False),
                "AvgCPUUtilization": safe_float(cpu_avg),
                "MaxCPUUtilization": cpu_max_val,
                "Description": f"RDS instance with low CPU utilization (≤20%) in the last {period} days",
            })
    
    fields = {
        "1": "InstanceName",
        "2": "InstanceType",
        "3": "Engine",
        "4": "EngineVersion",
        "5": "AvailabilityZone",
        "6": "MultiAZ",
        "7": "AvgCPUUtilization",
        "8": "MaxCPUUtilization",
        "9": "Description",
    }
    
    return {
        "id": 110,
        "name": "Underutilized RDS Instances",
        "fields": fields,
        "headers": fields_to_headers(fields),
        "count": len(underutilized_instances),
        "resource": underutilized_instances,
    }


def find_overutilized_rds_instances(
    session: Any, region_name: str, period: int, max_results: int = 100
) -> dict[str, Any]:
    """Find RDS instances with high CPU utilization."""
    rds_client = session.client("rds", region_name=region_name)
    cloudwatch_client = session.client("cloudwatch", region_name=region_name)
    
    start_time = datetime.now() - timedelta(days=period)
    end_time = datetime.now()
    
    # Get all RDS instances
    response = rds_client.describe_db_instances(MaxRecords=max_results)
    overutilized_instances = []
    
    for db_instance in response["DBInstances"]:
        db_instance_id = db_instance["DBInstanceIdentifier"]
        db_instance_class = db_instance["DBInstanceClass"]
        
        # Get CPU metrics
        cpu_datapoints = get_metric_statistics(
            cloudwatch_client,
            "AWS/RDS",
            "CPUUtilization",
            [{"Name": "DBInstanceIdentifier", "Value": db_instance_id}],
            start_time,
            end_time,
        )
        
        cpu_avg, cpu_min, cpu_max = calculate_metrics(cpu_datapoints)
        cpu_max_val = safe_float(cpu_max)
        
        # Check if overutilized (max CPU >= 80%)
        if cpu_max_val >= 80.0:
            overutilized_instances.append({
                "InstanceName": db_instance_id,
                "InstanceType": db_instance_class,
                "Engine": db_instance.get("Engine", ""),
                "EngineVersion": db_instance.get("EngineVersion", ""),
                "AvailabilityZone": db_instance.get("AvailabilityZone", ""),
                "MultiAZ": db_instance.get("MultiAZ", False),
                "AvgCPUUtilization": safe_float(cpu_avg),
                "MaxCPUUtilization": cpu_max_val,
                "Description": f"RDS instance with high CPU utilization (≥80%) in the last {period} days",
            })
    
    fields = {
        "1": "InstanceName",
        "2": "InstanceType",
        "3": "Engine",
        "4": "EngineVersion",
        "5": "AvailabilityZone",
        "6": "MultiAZ",
        "7": "AvgCPUUtilization",
        "8": "MaxCPUUtilization",
        "9": "Description",
    }
    
    return {
        "id": 112,
        "name": "Overutilized RDS Instances",
        "fields": fields,
        "headers": fields_to_headers(fields),
        "count": len(overutilized_instances),
        "resource": overutilized_instances,
    }
