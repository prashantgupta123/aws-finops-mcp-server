"""Cleanup tools for identifying unused AWS resources."""

import logging
from datetime import datetime, timedelta
from typing import Any

from ..utils.helpers import fields_to_headers

logger = logging.getLogger(__name__)


def find_unused_lambda_functions(
    session: Any, region_name: str, period: int, max_results: int = 100
) -> dict[str, Any]:
    """Find Lambda functions with no invocations in the specified period."""
    lambda_client = session.client("lambda", region_name=region_name)
    cloudwatch_client = session.client("cloudwatch", region_name=region_name)
    
    start_time = datetime.now() - timedelta(days=period)
    end_time = datetime.now()
    output_data = []
    
    # Get all Lambda functions
    next_token = None
    while True:
        params = {"MaxItems": max_results}
        if next_token:
            params["Marker"] = next_token
        
        response = lambda_client.list_functions(**params)
        
        for function in response["Functions"]:
            function_name = function["FunctionName"]
            
            # Check CloudWatch metrics
            cloudwatch_response = cloudwatch_client.get_metric_statistics(
                Namespace="AWS/Lambda",
                MetricName="Invocations",
                Dimensions=[{"Name": "FunctionName", "Value": function_name}],
                StartTime=start_time,
                EndTime=end_time,
                Period=86400,
                Statistics=["Sum"],
            )
            
            if not cloudwatch_response["Datapoints"]:
                # Calculate estimated monthly cost (storage + ephemeral storage)
                code_size_mb = function.get("CodeSize", 0) / (1024 * 1024)
                memory_mb = function.get("MemorySize", 128)
                # Storage: $0.0000000309/GB-second, Ephemeral: $0.0000000309/GB-second
                storage_cost = code_size_mb / 1024 * 0.0000000309 * 2592000  # 30 days
                
                # Get tags
                try:
                    tags_response = lambda_client.list_tags(Resource=function["FunctionArn"])
                    tags = tags_response.get("Tags", {})
                    tags_str = ", ".join([f"{k}={v}" for k, v in tags.items()]) if tags else "None"
                except Exception:
                    tags_str = "N/A"
                
                output_data.append({
                    "FunctionName": function_name,
                    "FunctionArn": function.get("FunctionArn", ""),
                    "Runtime": function.get("Runtime", "N/A"),
                    "MemorySize": f"{memory_mb} MB",
                    "CodeSize": f"{code_size_mb:.2f} MB",
                    "Timeout": f"{function.get('Timeout', 0)} sec",
                    "Handler": function.get("Handler", "N/A"),
                    "Role": function.get("Role", "").split("/")[-1] if function.get("Role") else "N/A",
                    "LastModified": function.get("LastModified", ""),
                    "VpcId": function.get("VpcConfig", {}).get("VpcId", "None"),
                    "EstimatedMonthlyCost": f"${storage_cost:.4f}",
                    "Tags": tags_str,
                    "Description": f"Lambda function not invoked in the last {period} days",
                })
        
        next_token = response.get("NextMarker")
        if not next_token:
            break
    
    fields = {
        "1": "FunctionName",
        "2": "FunctionArn",
        "3": "Runtime",
        "4": "MemorySize",
        "5": "CodeSize",
        "6": "Timeout",
        "7": "Handler",
        "8": "Role",
        "9": "LastModified",
        "10": "VpcId",
        "11": "EstimatedMonthlyCost",
        "12": "Tags",
        "13": "Description",
    }
    
    return {
        "id": 101,
        "name": "Unused Lambda Functions",
        "fields": fields,
        "headers": fields_to_headers(fields),
        "count": len(output_data),
        "resource": output_data,
    }


def find_unused_elastic_ips(session: Any, region_name: str) -> dict[str, Any]:
    """Find unattached Elastic IPs."""
    ec2_client = session.client("ec2", region_name=region_name)
    
    elastic_ips = ec2_client.describe_addresses()["Addresses"]
    unused_elastic_ips = [
        ip for ip in elastic_ips
        if "InstanceId" not in ip and "AssociationId" not in ip
    ]
    
    unused_elastic_ip_info = []
    for ip in unused_elastic_ips:
        # Get all tags
        tags = ip.get("Tags", [])
        name = None
        tags_str = "None"
        if tags:
            tags_dict = {tag["Key"]: tag["Value"] for tag in tags}
            name = tags_dict.get("Name")
            tags_str = ", ".join([f"{k}={v}" for k, v in tags_dict.items()])
        
        # Elastic IP cost: $0.005/hour = ~$3.60/month when not attached
        monthly_cost = 0.005 * 24 * 30
        
        ip_info = {
            "PublicIp": ip["PublicIp"],
            "AllocationId": ip["AllocationId"],
            "Name": name or "N/A",
            "Domain": ip.get("Domain", "vpc"),
            "NetworkBorderGroup": ip.get("NetworkBorderGroup", region_name),
            "PublicIpv4Pool": ip.get("PublicIpv4Pool", "amazon"),
            "PrivateIpAddress": ip.get("PrivateIpAddress", "None"),
            "CustomerOwnedIp": ip.get("CustomerOwnedIp", "None"),
            "EstimatedMonthlyCost": f"${monthly_cost:.2f}",
            "Tags": tags_str,
            "Description": "Unused Elastic IP - not attached to any instance",
        }
        
        unused_elastic_ip_info.append(ip_info)
    
    # Calculate total potential savings
    total_monthly_cost = len(unused_elastic_ip_info) * 3.60
    
    fields = {
        "1": "PublicIp",
        "2": "AllocationId",
        "3": "Name",
        "4": "Domain",
        "5": "NetworkBorderGroup",
        "6": "PublicIpv4Pool",
        "7": "PrivateIpAddress",
        "8": "EstimatedMonthlyCost",
        "9": "Tags",
        "10": "Description",
    }
    
    return {
        "id": 106,
        "name": "Unused Elastic IPs",
        "fields": fields,
        "headers": fields_to_headers(fields),
        "count": len(unused_elastic_ip_info),
        "total_monthly_cost": f"${total_monthly_cost:.2f}",
        "resource": unused_elastic_ip_info,
    }


def find_unused_amis(
    session: Any, region_name: str, period: int, max_results: int = 100
) -> dict[str, Any]:
    """Find AMIs not used by any EC2 instances, ASGs, or Spot Fleet Requests."""
    ec2_client = session.client("ec2", region_name=region_name)
    asg_client = session.client("autoscaling", region_name=region_name)
    
    cutoff_date = datetime.now() - timedelta(days=period)
    
    # Get all AMIs owned by account
    ami_names = {}
    response = ec2_client.describe_images(Owners=["self"], MaxResults=max_results)
    
    for image in response["Images"]:
        snap_list = []
        for snap in image["BlockDeviceMappings"]:
            if "Ebs" in snap and "SnapshotId" in snap["Ebs"]:
                snap_list.append(str(snap["Ebs"]["SnapshotId"]))
        
        ami_names[image["ImageId"]] = {
            "Name": image["Name"],
            "CreationDate": image["CreationDate"],
            "Snapshots": snap_list,
            "Platform": image.get("Platform", "Linux/UNIX"),
            "Architecture": image.get("Architecture", "N/A"),
        }
    
    # Get AMIs in use by EC2 instances
    ec2_amis = set()
    response = ec2_client.describe_instances(MaxResults=max_results)
    for reservation in response["Reservations"]:
        for instance in reservation["Instances"]:
            ec2_amis.add(instance["ImageId"])
    
    # Get AMIs in use by ASGs
    asg_amis = set()
    response = asg_client.describe_auto_scaling_groups(MaxRecords=max_results)
    for asg in response["AutoScalingGroups"]:
        if "LaunchTemplate" in asg:
            lt_id = asg["LaunchTemplate"]["LaunchTemplateId"]
            lt_version = asg["LaunchTemplate"]["Version"]
            try:
                lt_response = ec2_client.describe_launch_template_versions(
                    LaunchTemplateId=lt_id, Versions=[lt_version]
                )
                for version in lt_response["LaunchTemplateVersions"]:
                    if "ImageId" in version["LaunchTemplateData"]:
                        asg_amis.add(version["LaunchTemplateData"]["ImageId"])
            except Exception as e:
                logger.warning(f"Error getting launch template for ASG: {e}")
        elif "MixedInstancesPolicy" in asg:
            lt_id = asg["MixedInstancesPolicy"]["LaunchTemplate"]["LaunchTemplateSpecification"]["LaunchTemplateId"]
            lt_version = asg["MixedInstancesPolicy"]["LaunchTemplate"]["LaunchTemplateSpecification"]["Version"]
            try:
                lt_response = ec2_client.describe_launch_template_versions(
                    LaunchTemplateId=lt_id, Versions=[lt_version]
                )
                for version in lt_response["LaunchTemplateVersions"]:
                    if "ImageId" in version["LaunchTemplateData"]:
                        asg_amis.add(version["LaunchTemplateData"]["ImageId"])
            except Exception as e:
                logger.warning(f"Error getting launch template for ASG with mixed instances: {e}")
    
    # Get AMIs in use by Spot Fleet Requests
    spot_fleet_amis = set()
    try:
        spot_response = ec2_client.describe_spot_fleet_requests(MaxResults=max_results)
        for spot_request in spot_response.get("SpotFleetRequestConfigs", []):
            spot_config = spot_request.get("SpotFleetRequestConfig", {})
            
            # Check LaunchSpecifications (older format)
            if "LaunchSpecifications" in spot_config:
                for launch_spec in spot_config["LaunchSpecifications"]:
                    if "ImageId" in launch_spec:
                        spot_fleet_amis.add(launch_spec["ImageId"])
            
            # Check LaunchTemplateConfigs (newer format)
            elif "LaunchTemplateConfigs" in spot_config:
                for lt_config in spot_config["LaunchTemplateConfigs"]:
                    lt_spec = lt_config.get("LaunchTemplateSpecification", {})
                    if "LaunchTemplateName" in lt_spec:
                        lt_name = lt_spec["LaunchTemplateName"]
                        lt_version = lt_spec.get("Version", "$Latest")
                        try:
                            lt_response = ec2_client.describe_launch_template_versions(
                                LaunchTemplateName=lt_name,
                                Versions=[lt_version]
                            )
                            for version in lt_response["LaunchTemplateVersions"]:
                                if "ImageId" in version["LaunchTemplateData"]:
                                    spot_fleet_amis.add(version["LaunchTemplateData"]["ImageId"])
                        except Exception as e:
                            logger.debug(f"Error getting launch template for Spot Fleet: {e}")
                    elif "LaunchTemplateId" in lt_spec:
                        lt_id = lt_spec["LaunchTemplateId"]
                        lt_version = lt_spec.get("Version", "$Latest")
                        try:
                            lt_response = ec2_client.describe_launch_template_versions(
                                LaunchTemplateId=lt_id,
                                Versions=[lt_version]
                            )
                            for version in lt_response["LaunchTemplateVersions"]:
                                if "ImageId" in version["LaunchTemplateData"]:
                                    spot_fleet_amis.add(version["LaunchTemplateData"]["ImageId"])
                        except Exception as e:
                            logger.debug(f"Error getting launch template for Spot Fleet: {e}")
    except Exception as e:
        logger.warning(f"Error getting Spot Fleet Requests: {e}")
    
    # Get AMIs in use by Launch Templates
    launch_template_amis = set()
    try:
        lt_response = ec2_client.describe_launch_templates(MaxResults=max_results)
        for template in lt_response.get("LaunchTemplates", []):
            try:
                template_versions = ec2_client.describe_launch_template_versions(
                    LaunchTemplateId=template["LaunchTemplateId"]
                )
                for version in template_versions.get("LaunchTemplateVersions", []):
                    if "ImageId" in version.get("LaunchTemplateData", {}):
                        launch_template_amis.add(version["LaunchTemplateData"]["ImageId"])
            except Exception as e:
                logger.debug(f"Error retrieving launch template version: {e}")
    except Exception as e:
        logger.warning(f"Error getting Launch Templates: {e}")
    
    # Get volume snapshot map
    volume_snapshot_map = {}
    response = ec2_client.describe_volumes(MaxResults=max_results)
    for volume in response["Volumes"]:
        if "SnapshotId" in volume and volume["SnapshotId"]:
            volume_snapshot_map[volume["VolumeId"]] = volume["SnapshotId"]
    
    # Get snapshot sizes for cost calculation
    snapshot_sizes = {}
    for image_id, details in ami_names.items():
        for snap_id in details["Snapshots"]:
            try:
                snap_response = ec2_client.describe_snapshots(SnapshotIds=[snap_id])
                if snap_response["Snapshots"]:
                    snapshot_sizes[snap_id] = snap_response["Snapshots"][0].get("VolumeSize", 0)
            except Exception:
                snapshot_sizes[snap_id] = 0
    
    # Find unused AMIs
    output_json = []
    for image_id, details in ami_names.items():
        creation_date = datetime.strptime(details["CreationDate"], "%Y-%m-%dT%H:%M:%S.%fZ")
        
        # Skip if AMI is in use or too new or is AWS Backup
        if (
            image_id in ec2_amis
            or image_id in asg_amis
            or image_id in spot_fleet_amis
            or image_id in launch_template_amis
            or creation_date >= cutoff_date
            or details["Name"].startswith("AwsBackup_")
        ):
            continue
        
        # Check if snapshots are in use
        snapshot_in_use = any(
            snapshot in volume_snapshot_map.values()
            for snapshot in details["Snapshots"]
        )
        
        if not snapshot_in_use:
            age_days = (datetime.now() - creation_date).days
            
            # Calculate total snapshot size and cost
            total_size_gb = sum(snapshot_sizes.get(snap, 0) for snap in details["Snapshots"])
            # Snapshot cost: $0.05/GB/month
            estimated_cost = total_size_gb * 0.05
            
            # Get AMI details for additional fields
            try:
                ami_detail = ec2_client.describe_images(ImageIds=[image_id])["Images"][0]
                state = ami_detail.get("State", "N/A")
                image_type = ami_detail.get("ImageType", "N/A")
                root_device_type = ami_detail.get("RootDeviceType", "N/A")
                virtualization_type = ami_detail.get("VirtualizationType", "N/A")
                owner_id = ami_detail.get("OwnerId", "N/A")
                
                # Get tags
                tags = ami_detail.get("Tags", [])
                tags_str = ", ".join([f"{tag['Key']}={tag['Value']}" for tag in tags]) if tags else "None"
            except Exception:
                state = "N/A"
                image_type = "N/A"
                root_device_type = "N/A"
                virtualization_type = "N/A"
                owner_id = "N/A"
                tags_str = "N/A"
            
            output_json.append({
                "ImageId": image_id,
                "Name": details["Name"],
                "State": state,
                "ImageType": image_type,
                "CreationDate": details["CreationDate"],
                "Age": f"{age_days} days",
                "Platform": details["Platform"],
                "Architecture": details["Architecture"],
                "RootDeviceType": root_device_type,
                "VirtualizationType": virtualization_type,
                "OwnerId": owner_id,
                "SnapshotCount": len(details["Snapshots"]),
                "TotalSnapshotSizeGB": total_size_gb,
                "EstimatedMonthlyCost": f"${estimated_cost:.2f}",
                "Snapshots": ", ".join(details["Snapshots"]),
                "Tags": tags_str,
                "Description": f"AMI not used by any EC2 instances, Auto Scaling Groups, Spot Fleet Requests, or Launch Templates",
            })
    
    # Calculate total potential savings
    total_monthly_cost = sum(
        float(ami["EstimatedMonthlyCost"].replace("$", ""))
        for ami in output_json
    )
    
    fields = {
        "1": "ImageId",
        "2": "Name",
        "3": "State",
        "4": "CreationDate",
        "5": "Age",
        "6": "Platform",
        "7": "Architecture",
        "8": "RootDeviceType",
        "9": "VirtualizationType",
        "10": "SnapshotCount",
        "11": "TotalSnapshotSizeGB",
        "12": "EstimatedMonthlyCost",
        "13": "Tags",
        "14": "Description",
    }
    
    return {
        "id": 107,
        "name": "Unused AMIs",
        "fields": fields,
        "headers": fields_to_headers(fields),
        "count": len(output_json),
        "total_monthly_cost": f"${total_monthly_cost:.2f}",
        "resource": output_json,
    }



def find_unused_load_balancers(
    session: Any, region_name: str, period: int
) -> dict[str, Any]:
    """Find load balancers with no traffic in the specified period."""
    elb_client = session.client("elbv2", region_name=region_name)
    cloudwatch_client = session.client("cloudwatch", region_name=region_name)
    
    start_time = datetime.now() - timedelta(days=period)
    end_time = datetime.now()
    unused_elbs = []
    
    response = elb_client.describe_load_balancers()
    
    for lb in response["LoadBalancers"]:
        lb_name = lb["LoadBalancerArn"].split("loadbalancer/")[1]
        lb_type = "NLB" if lb["Type"] == "network" else "ALB"
        
        # Check CloudWatch metrics based on type
        if lb_type == "ALB":
            cloudwatch_response = cloudwatch_client.get_metric_statistics(
                Namespace="AWS/ApplicationELB",
                MetricName="RequestCount",
                Dimensions=[{"Name": "LoadBalancer", "Value": lb_name}],
                StartTime=start_time,
                EndTime=end_time,
                Period=86400,
                Statistics=["Sum"],
            )
            
            # Double-check with fixed response count
            if not cloudwatch_response["Datapoints"]:
                cloudwatch_response = cloudwatch_client.get_metric_statistics(
                    Namespace="AWS/ApplicationELB",
                    MetricName="HTTP_Fixed_Response_Count",
                    Dimensions=[{"Name": "LoadBalancer", "Value": lb_name}],
                    StartTime=start_time,
                    EndTime=end_time,
                    Period=86400,
                    Statistics=["Sum"],
                )
        else:  # NLB
            cloudwatch_response = cloudwatch_client.get_metric_statistics(
                Namespace="AWS/NetworkELB",
                MetricName="ActiveFlowCount_TCP",
                Dimensions=[{"Name": "LoadBalancer", "Value": lb_name}],
                StartTime=start_time,
                EndTime=end_time,
                Period=86400,
                Statistics=["Sum"],
            )
        
        if not cloudwatch_response["Datapoints"]:
            # Calculate age
            created_time = lb.get("CreatedTime")
            age_days = 0
            if created_time:
                age_days = (datetime.now(created_time.tzinfo) - created_time).days
            
            # Estimate monthly cost: ALB ~$22.50, NLB ~$32.40 per month (base cost)
            monthly_cost = 32.40 if lb_type == "NLB" else 22.50
            
            # Get availability zones
            azs = [az["ZoneName"] for az in lb.get("AvailabilityZones", [])]
            azs_str = ", ".join(azs) if azs else "N/A"
            
            # Get security groups
            sgs = lb.get("SecurityGroups", [])
            sgs_str = ", ".join(sgs) if sgs else "None"
            
            # Get tags
            try:
                tags_response = elb_client.describe_tags(ResourceArns=[lb["LoadBalancerArn"]])
                tags = tags_response.get("TagDescriptions", [{}])[0].get("Tags", [])
                tags_str = ", ".join([f"{tag['Key']}={tag['Value']}" for tag in tags]) if tags else "None"
            except Exception:
                tags_str = "N/A"
            
            # Get target groups count
            try:
                tg_response = elb_client.describe_target_groups(LoadBalancerArn=lb["LoadBalancerArn"])
                tg_count = len(tg_response.get("TargetGroups", []))
            except Exception:
                tg_count = 0
            
            unused_elbs.append({
                "Name": lb_name,
                "LoadBalancerArn": lb["LoadBalancerArn"],
                "Type": lb_type,
                "State": lb.get("State", {}).get("Code", "N/A"),
                "DNSName": lb.get("DNSName", ""),
                "Scheme": lb.get("Scheme", ""),
                "VpcId": lb.get("VpcId", ""),
                "AvailabilityZones": azs_str,
                "SecurityGroups": sgs_str,
                "IpAddressType": lb.get("IpAddressType", "ipv4"),
                "CreatedTime": created_time.strftime("%Y-%m-%d %H:%M:%S") if created_time else "N/A",
                "AgeDays": age_days,
                "TargetGroupCount": tg_count,
                "EstimatedMonthlyCost": f"${monthly_cost:.2f}",
                "Tags": tags_str,
                "Description": f"Load Balancer with no traffic in the last {period} days",
            })
    
    # Calculate total potential savings
    total_monthly_cost = sum(
        float(lb["EstimatedMonthlyCost"].replace("$", ""))
        for lb in unused_elbs
    )
    
    fields = {
        "1": "Name",
        "2": "LoadBalancerArn",
        "3": "Type",
        "4": "State",
        "5": "DNSName",
        "6": "Scheme",
        "7": "VpcId",
        "8": "AvailabilityZones",
        "9": "SecurityGroups",
        "10": "IpAddressType",
        "11": "CreatedTime",
        "12": "AgeDays",
        "13": "TargetGroupCount",
        "14": "EstimatedMonthlyCost",
        "15": "Tags",
        "16": "Description",
    }
    
    return {
        "id": 103,
        "name": "Unused Load Balancers",
        "fields": fields,
        "headers": fields_to_headers(fields),
        "count": len(unused_elbs),
        "total_monthly_cost": f"${total_monthly_cost:.2f}",
        "resource": unused_elbs,
    }


def find_unused_target_groups(
    session: Any, region_name: str, period: int = 7, max_results: int = 100
) -> dict[str, Any]:
    """Find target groups with no registered targets or no traffic.
    
    This function identifies target groups that are:
    1. Not attached to any load balancer, OR
    2. Have no registered targets, OR
    3. Have registered targets but no traffic in the specified period
    
    Args:
        session: Boto3 session
        region_name: AWS region name
        period: Lookback period in days for traffic check (default: 7)
        max_results: Maximum results per API call
    
    Returns:
        Dictionary with unused target groups
    """
    elb_client = session.client("elbv2", region_name=region_name)
    cloudwatch_client = session.client("cloudwatch", region_name=region_name)
    
    start_time = datetime.now() - timedelta(days=period)
    end_time = datetime.now()
    
    unused_tgs = []
    next_token = None
    
    logger.info(f"Finding unused target groups in {region_name}")
    
    while True:
        params = {"PageSize": max_results}
        if next_token:
            params["Marker"] = next_token
        
        response = elb_client.describe_target_groups(**params)
        
        for tg in response["TargetGroups"]:
            tg_arn = tg["TargetGroupArn"]
            tg_name = tg["TargetGroupName"]
            lb_arns = tg.get("LoadBalancerArns", [])
            
            is_unused = False
            reason = ""
            
            # Case 1: Not attached to any load balancer
            if not lb_arns:
                is_unused = True
                reason = "Not attached to any load balancer"
            else:
                # Case 2: Check if target group has registered targets
                health_response = elb_client.describe_target_health(TargetGroupArn=tg_arn)
                
                if not health_response["TargetHealthDescriptions"]:
                    is_unused = True
                    reason = "No registered targets"
                else:
                    # Case 3: Has targets but check for traffic via CloudWatch
                    # Extract target group and load balancer identifiers for CloudWatch
                    tg_identifier = "targetgroup/" + tg_arn.split("targetgroup/")[1]
                    lb_identifier = lb_arns[0].split("loadbalancer/")[1]
                    
                    has_traffic = _check_target_group_traffic(
                        cloudwatch_client, tg_identifier, lb_identifier, start_time, end_time
                    )
                    
                    if not has_traffic:
                        is_unused = True
                        reason = f"No traffic in the last {period} days"
            
            if is_unused:
                lb_arns_str = ", ".join([arn.split("/")[-1] for arn in lb_arns]) if lb_arns else "None"
                
                # Get health check configuration
                health_check_protocol = tg.get("HealthCheckProtocol", "N/A")
                health_check_path = tg.get("HealthCheckPath", "N/A")
                health_check_interval = tg.get("HealthCheckIntervalSeconds", 0)
                matcher = tg.get("Matcher", {})
                matcher_str = str(matcher.get("HttpCode", "N/A")) if matcher else "N/A"
                
                # Get tags
                try:
                    tags_response = elb_client.describe_tags(ResourceArns=[tg_arn])
                    tags = tags_response.get("TagDescriptions", [{}])[0].get("Tags", [])
                    tags_str = ", ".join([f"{tag['Key']}={tag['Value']}" for tag in tags]) if tags else "None"
                except Exception:
                    tags_str = "N/A"
                
                unused_tgs.append({
                    "TargetGroupName": tg_name,
                    "TargetGroupArn": tg_arn,
                    "TargetType": tg.get("TargetType", "instance"),
                    "Protocol": tg.get("Protocol", ""),
                    "Port": tg.get("Port", 0),
                    "VpcId": tg.get("VpcId", ""),
                    "HealthCheckProtocol": health_check_protocol,
                    "HealthCheckPath": health_check_path,
                    "HealthCheckIntervalSeconds": health_check_interval,
                    "Matcher": matcher_str,
                    "LoadBalancerCount": len(lb_arns),
                    "LoadBalancerArns": lb_arns_str,
                    "Tags": tags_str,
                    "Reason": reason,
                    "Description": f"Target group unused: {reason}",
                })
        
        next_token = response.get("NextMarker")
        if not next_token:
            break
    
    fields = {
        "1": "TargetGroupName",
        "2": "TargetGroupArn",
        "3": "TargetType",
        "4": "Protocol",
        "5": "Port",
        "6": "VpcId",
        "7": "HealthCheckProtocol",
        "8": "HealthCheckPath",
        "9": "HealthCheckIntervalSeconds",
        "10": "Matcher",
        "11": "LoadBalancerCount",
        "12": "LoadBalancerArns",
        "13": "Tags",
        "14": "Reason",
        "15": "Description",
    }
    
    return {
        "id": 104,
        "name": "Unused Target Groups",
        "fields": fields,
        "headers": fields_to_headers(fields),
        "count": len(unused_tgs),
        "resource": unused_tgs,
    }


def _check_target_group_traffic(
    cloudwatch_client: Any,
    tg_identifier: str,
    lb_identifier: str,
    start_time: datetime,
    end_time: datetime
) -> bool:
    """Check if target group has received any traffic via CloudWatch metrics.
    
    Args:
        cloudwatch_client: CloudWatch client
        tg_identifier: Target group identifier (targetgroup/name/id)
        lb_identifier: Load balancer identifier (app/name/id)
        start_time: Start time for metric query
        end_time: End time for metric query
    
    Returns:
        True if target group has traffic, False otherwise
    """
    try:
        # Check RequestCount metric
        response = cloudwatch_client.get_metric_statistics(
            Namespace="AWS/ApplicationELB",
            MetricName="RequestCount",
            Dimensions=[
                {"Name": "TargetGroup", "Value": tg_identifier},
                {"Name": "LoadBalancer", "Value": lb_identifier}
            ],
            StartTime=start_time,
            EndTime=end_time,
            Period=86400,  # Daily aggregation
            Statistics=["Sum"]
        )
        
        # If we have datapoints with non-zero values, there's traffic
        if response.get("Datapoints"):
            total_requests = sum(point["Sum"] for point in response["Datapoints"])
            if total_requests > 0:
                return True
        
        return False
    
    except Exception as e:
        logger.debug(f"Error checking traffic for target group {tg_identifier}: {e}")
        # If we can't check metrics, assume it has traffic to be safe
        return True


def find_unused_log_groups(
    session: Any, region_name: str, period: int, max_results: int = 50
) -> dict[str, Any]:
    """Find CloudWatch Log Groups with no recent log events.
    
    This function checks the most recent log stream's lastIngestionTime
    to accurately determine if a log group is unused.
    """
    logs_client = session.client("logs", region_name=region_name)
    
    threshold = datetime.now() - timedelta(days=period)
    unused_log_groups = []
    next_token = None
    
    logger.info(f"Finding unused log groups in {region_name}")
    
    while True:
        params = {"limit": max_results}
        if next_token:
            params["nextToken"] = next_token
        
        response = logs_client.describe_log_groups(**params)
        
        for log_group in response["logGroups"]:
            log_group_name = log_group["logGroupName"]
            
            # Get the most recent log stream
            is_unused = False
            try:
                log_streams_response = logs_client.describe_log_streams(
                    logGroupName=log_group_name,
                    orderBy="LastEventTime",
                    descending=True,
                    limit=1
                )
                
                log_streams = log_streams_response.get("logStreams", [])
                
                # If no log streams, log group is unused
                if not log_streams:
                    is_unused = True
                else:
                    most_recent_stream = log_streams[0]
                    
                    # Check lastIngestionTime
                    if "lastIngestionTime" in most_recent_stream:
                        latest_ingestion_time = most_recent_stream["lastIngestionTime"]
                        latest_ingestion_datetime = datetime.fromtimestamp(latest_ingestion_time / 1000)
                        
                        if latest_ingestion_datetime < threshold:
                            is_unused = True
                    else:
                        # No ingestion time means no logs ingested
                        is_unused = True
            
            except Exception as e:
                logger.debug(f"Error checking log streams for {log_group_name}: {e}")
                # If we can't check log streams, fall back to log group's lastEventTime
                last_event_time = log_group.get("lastEventTime", 0)
                cutoff_time = int(threshold.timestamp() * 1000)
                if last_event_time < cutoff_time:
                    is_unused = True
            
            if is_unused:
                stored_bytes = log_group.get("storedBytes", 0)
                stored_mb = stored_bytes / (1024 * 1024)
                stored_gb = stored_mb / 1024
                
                # CloudWatch Logs cost: $0.50/GB/month
                estimated_cost = stored_gb * 0.50
                
                # Calculate age and days since last event
                creation_time = log_group.get("creationTime", 0) / 1000
                age_days = (datetime.now().timestamp() - creation_time) / 86400 if creation_time > 0 else 0
                
                last_event_time = log_group.get("lastEventTime", 0)
                days_since_last_event = (datetime.now().timestamp() - (last_event_time / 1000)) / 86400 if last_event_time > 0 else 0
                
                # Get log group ARN
                log_group_arn = log_group.get("arn", "N/A")
                
                # Get KMS key
                kms_key_id = log_group.get("kmsKeyId", "None")
                
                # Get metric filters count
                try:
                    metric_filters = logs_client.describe_metric_filters(
                        logGroupName=log_group_name
                    )
                    metric_filter_count = len(metric_filters.get("metricFilters", []))
                except Exception:
                    metric_filter_count = 0
                
                unused_log_groups.append({
                    "LogGroupName": log_group_name,
                    "LogGroupArn": log_group_arn,
                    "CreationTime": datetime.fromtimestamp(creation_time).isoformat() if creation_time > 0 else "N/A",
                    "AgeDays": int(age_days),
                    "LastEventTime": datetime.fromtimestamp(last_event_time / 1000).isoformat()
                    if last_event_time > 0
                    else "Never",
                    "DaysSinceLastEvent": int(days_since_last_event) if last_event_time > 0 else "N/A",
                    "StoredMB": f"{stored_mb:.2f}",
                    "RetentionDays": log_group.get("retentionInDays", "Never Expire"),
                    "KmsKeyId": kms_key_id.split("/")[-1] if kms_key_id != "None" else "None",
                    "MetricFilterCount": metric_filter_count,
                    "EstimatedMonthlyCost": f"${estimated_cost:.4f}",
                    "Description": f"Log group with no log ingestion in the last {period} days",
                })
        
        next_token = response.get("nextToken")
        if not next_token:
            break
    
    # Calculate total potential savings
    total_monthly_cost = sum(
        float(lg["EstimatedMonthlyCost"].replace("$", ""))
        for lg in unused_log_groups
    )
    
    fields = {
        "1": "LogGroupName",
        "2": "LogGroupArn",
        "3": "CreationTime",
        "4": "AgeDays",
        "5": "LastEventTime",
        "6": "DaysSinceLastEvent",
        "7": "StoredMB",
        "8": "RetentionDays",
        "9": "KmsKeyId",
        "10": "MetricFilterCount",
        "11": "EstimatedMonthlyCost",
        "12": "Description",
    }
    
    return {
        "id": 105,
        "name": "Unused Log Groups",
        "fields": fields,
        "headers": fields_to_headers(fields),
        "count": len(unused_log_groups),
        "total_monthly_cost": f"${total_monthly_cost:.4f}",
        "resource": unused_log_groups,
    }


def find_unused_snapshots(
    session: Any, region_name: str, period: int, max_results: int = 100
) -> dict[str, Any]:
    """Find EBS snapshots not associated with any AMI or volume."""
    ec2_client = session.client("ec2", region_name=region_name)
    
    cutoff_date = datetime.now(tz=None) - timedelta(days=period)
    
    # Get all snapshots owned by account
    response = ec2_client.describe_snapshots(OwnerIds=["self"], MaxResults=max_results)
    all_snapshots = response["Snapshots"]
    
    # Get snapshots used by AMIs
    ami_snapshots = set()
    ami_response = ec2_client.describe_images(Owners=["self"], MaxResults=max_results)
    for image in ami_response["Images"]:
        for bdm in image["BlockDeviceMappings"]:
            if "Ebs" in bdm and "SnapshotId" in bdm["Ebs"]:
                ami_snapshots.add(bdm["Ebs"]["SnapshotId"])
    
    # Get snapshots used by volumes
    volume_snapshots = set()
    volume_response = ec2_client.describe_volumes(MaxResults=max_results)
    for volume in volume_response["Volumes"]:
        if "SnapshotId" in volume and volume["SnapshotId"]:
            volume_snapshots.add(volume["SnapshotId"])
    
    unused_snapshots = []
    for snapshot in all_snapshots:
        snapshot_id = snapshot["SnapshotId"]
        start_time = snapshot["StartTime"].replace(tzinfo=None)
        
        # Skip if snapshot is in use or too new or is AWS Backup
        description = snapshot.get("Description", "")
        if (
            snapshot_id in ami_snapshots
            or snapshot_id in volume_snapshots
            or start_time >= cutoff_date
            or "Created by CreateImage" in description
            or "AwsBackup" in description
        ):
            continue
        
        age_days = (datetime.now() - start_time).days
        size_gb = snapshot.get("VolumeSize", 0)
        
        # Snapshot cost: $0.05/GB/month
        estimated_cost = size_gb * 0.05
        
        # Get additional snapshot details
        owner_id = snapshot.get("OwnerId", "N/A")
        encrypted = snapshot.get("Encrypted", False)
        kms_key_id = snapshot.get("KmsKeyId", "None")
        data_encryption_key_id = snapshot.get("DataEncryptionKeyId", "None")
        progress = snapshot.get("Progress", "N/A")
        outpost_arn = snapshot.get("OutpostArn", "None")
        
        # Get tags
        tags = snapshot.get("Tags", [])
        tags_str = ", ".join([f"{tag['Key']}={tag['Value']}" for tag in tags]) if tags else "None"
        
        unused_snapshots.append({
            "SnapshotId": snapshot_id,
            "Description": description,
            "StartTime": start_time.isoformat(),
            "Age": f"{age_days} days",
            "SizeGB": size_gb,
            "VolumeId": snapshot.get("VolumeId", ""),
            "State": snapshot.get("State", ""),
            "Progress": progress,
            "OwnerId": owner_id,
            "Encrypted": encrypted,
            "KmsKeyId": kms_key_id.split("/")[-1] if kms_key_id != "None" else "None",
            "OutpostArn": outpost_arn,
            "EstimatedMonthlyCost": f"${estimated_cost:.2f}",
            "Tags": tags_str,
        })
    
    # Calculate total potential savings
    total_monthly_cost = sum(
        float(snap["EstimatedMonthlyCost"].replace("$", ""))
        for snap in unused_snapshots
    )
    
    fields = {
        "1": "SnapshotId",
        "2": "Description",
        "3": "StartTime",
        "4": "Age",
        "5": "SizeGB",
        "6": "VolumeId",
        "7": "State",
        "8": "Progress",
        "9": "OwnerId",
        "10": "Encrypted",
        "11": "KmsKeyId",
        "12": "EstimatedMonthlyCost",
        "13": "Tags",
    }
    
    return {
        "id": 108,
        "name": "Unused Snapshots",
        "fields": fields,
        "headers": fields_to_headers(fields),
        "count": len(unused_snapshots),
        "total_monthly_cost": f"${total_monthly_cost:.2f}",
        "resource": unused_snapshots,
    }


def find_unused_security_groups(
    session: Any, region_name: str, max_results: int = 100
) -> dict[str, Any]:
    """Find security groups not attached to any resources."""
    ec2_client = session.client("ec2", region_name=region_name)
    lambda_client = session.client("lambda", region_name=region_name)
    elb_client = session.client("elbv2", region_name=region_name)
    rds_client = session.client("rds", region_name=region_name)
    asg_client = session.client("autoscaling", region_name=region_name)
    
    # Get all security groups
    sg_dict = {}
    sg_set = set()
    response = ec2_client.describe_security_groups(MaxResults=max_results)
    for sg in response["SecurityGroups"]:
        sg_dict[sg["GroupId"]] = sg
        sg_set.add(sg["GroupId"])
    
    # Get SGs in use by EC2 instances
    used_sgs = set()
    response = ec2_client.describe_instances(MaxResults=max_results)
    for reservation in response["Reservations"]:
        for instance in reservation["Instances"]:
            for sg in instance["SecurityGroups"]:
                used_sgs.add(sg["GroupId"])
    
    # Get SGs in use by network interfaces
    response = ec2_client.describe_network_interfaces(MaxResults=max_results)
    for nic in response["NetworkInterfaces"]:
        for sg in nic["Groups"]:
            used_sgs.add(sg["GroupId"])
    
    # Get SGs in use by RDS
    response = rds_client.describe_db_instances(MaxRecords=max_results)
    for db in response["DBInstances"]:
        for sg in db["VpcSecurityGroups"]:
            used_sgs.add(sg["VpcSecurityGroupId"])
    
    # Get SGs in use by load balancers
    response = elb_client.describe_load_balancers(PageSize=max_results)
    for lb in response["LoadBalancers"]:
        if "SecurityGroups" in lb:
            for sg in lb["SecurityGroups"]:
                used_sgs.add(sg)
    
    # Get SGs in use by Lambda
    response = lambda_client.list_functions(MaxItems=max_results)
    for func in response["Functions"]:
        if "VpcConfig" in func and func["VpcConfig"].get("SecurityGroupIds"):
            for sg in func["VpcConfig"]["SecurityGroupIds"]:
                used_sgs.add(sg)
    
    # Find unused security groups
    unused_sgs = sg_set - used_sgs
    output_json = []
    
    for sg_id in unused_sgs:
        sg_info = sg_dict[sg_id]
        # Skip default security groups
        if sg_info.get("GroupName") == "default":
            continue
        
        # Get owner ID
        owner_id = sg_info.get("OwnerId", "N/A")
        
        # Get tags
        tags = sg_info.get("Tags", [])
        tags_str = ", ".join([f"{tag['Key']}={tag['Value']}" for tag in tags]) if tags else "None"
        
        # Count rules
        inbound_count = len(sg_info.get("IpPermissions", []))
        outbound_count = len(sg_info.get("IpPermissionsEgress", []))
        total_rules = inbound_count + outbound_count
        
        # Check if referenced by other security groups
        referenced_by = []
        referencing = []
        
        for other_sg_id, other_sg_info in sg_dict.items():
            # Check if this SG is referenced by others
            for perm in other_sg_info.get("IpPermissions", []) + other_sg_info.get("IpPermissionsEgress", []):
                for user_id_group_pair in perm.get("UserIdGroupPairs", []):
                    if user_id_group_pair.get("GroupId") == sg_id:
                        referenced_by.append(other_sg_id)
            
            # Check if this SG references others
            for perm in sg_info.get("IpPermissions", []) + sg_info.get("IpPermissionsEgress", []):
                for user_id_group_pair in perm.get("UserIdGroupPairs", []):
                    ref_sg_id = user_id_group_pair.get("GroupId")
                    if ref_sg_id and ref_sg_id != sg_id:
                        referencing.append(ref_sg_id)
        
        referenced_by_str = ", ".join(set(referenced_by)) if referenced_by else "None"
        referencing_str = ", ".join(set(referencing)) if referencing else "None"
        
        output_json.append({
            "SecurityGroupID": sg_id,
            "SecurityGroupName": sg_info.get("GroupName", ""),
            "Description": sg_info.get("Description", ""),
            "VpcId": sg_info.get("VpcId", ""),
            "OwnerId": owner_id,
            "InboundRulesCount": inbound_count,
            "OutboundRulesCount": outbound_count,
            "TotalRulesCount": total_rules,
            "ReferencedBySecurityGroups": referenced_by_str,
            "ReferencingSecurityGroups": referencing_str,
            "Tags": tags_str,
        })
    
    fields = {
        "1": "SecurityGroupID",
        "2": "SecurityGroupName",
        "3": "Description",
        "4": "VpcId",
        "5": "OwnerId",
        "6": "InboundRulesCount",
        "7": "OutboundRulesCount",
        "8": "TotalRulesCount",
        "9": "ReferencedBySecurityGroups",
        "10": "ReferencingSecurityGroups",
        "11": "Tags",
    }
    
    return {
        "id": 114,
        "name": "Unused Security Groups",
        "fields": fields,
        "headers": fields_to_headers(fields),
        "count": len(output_json),
        "resource": output_json,
    }



def find_unused_volumes(
    session: Any, region_name: str, max_results: int = 100
) -> dict[str, Any]:
    """Find EBS volumes that are not attached to any instance.
    
    Args:
        session: Boto3 session
        region_name: AWS region name
        max_results: Maximum results to return
    
    Returns:
        Dictionary with unused EBS volumes
    """
    ec2_client = session.client("ec2", region_name=region_name)
    
    logger.info(f"Finding unused EBS volumes in {region_name}")
    
    output_data = []
    
    try:
        # Get all volumes with 'available' state (not attached)
        paginator = ec2_client.get_paginator("describe_volumes")
        page_iterator = paginator.paginate(
            Filters=[{"Name": "status", "Values": ["available"]}],
            PaginationConfig={"MaxItems": max_results}
        )
        
        for page in page_iterator:
            for volume in page["Volumes"]:
                volume_id = volume["VolumeId"]
                volume_size = volume["Size"]
                volume_type = volume["VolumeType"]
                create_time = volume["CreateTime"]
                
                # Calculate age in days
                age_days = (datetime.now(create_time.tzinfo) - create_time).days
                
                # Get volume name and all tags
                volume_name = None
                tags = volume.get("Tags", [])
                tags_dict = {}
                if tags:
                    tags_dict = {tag["Key"]: tag["Value"] for tag in tags}
                    volume_name = tags_dict.get("Name")
                tags_str = ", ".join([f"{k}={v}" for k, v in tags_dict.items()]) if tags_dict else "None"
                
                # Calculate estimated monthly cost
                # Rough estimates: gp3=$0.08/GB, gp2=$0.10/GB, io1=$0.125/GB, st1=$0.045/GB, sc1=$0.015/GB
                cost_per_gb = {
                    "gp3": 0.08,
                    "gp2": 0.10,
                    "io1": 0.125,
                    "io2": 0.125,
                    "st1": 0.045,
                    "sc1": 0.015,
                    "standard": 0.05,
                }
                monthly_cost = volume_size * cost_per_gb.get(volume_type, 0.10)
                
                # Get additional volume details
                iops = volume.get("Iops", "N/A")
                throughput = volume.get("Throughput", "N/A")
                snapshot_id = volume.get("SnapshotId", "None")
                kms_key_id = volume.get("KmsKeyId", "None")
                multi_attach_enabled = volume.get("MultiAttachEnabled", False)
                fast_restored = volume.get("FastRestored", False)
                outpost_arn = volume.get("OutpostArn", "None")
                
                output_data.append({
                    "VolumeId": volume_id,
                    "Name": volume_name or "N/A",
                    "Size": f"{volume_size} GB",
                    "VolumeType": volume_type,
                    "State": volume["State"],
                    "CreateTime": create_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "AgeDays": age_days,
                    "Iops": iops,
                    "Throughput": throughput,
                    "SnapshotId": snapshot_id,
                    "EstimatedMonthlyCost": f"${monthly_cost:.2f}",
                    "AvailabilityZone": volume["AvailabilityZone"],
                    "Encrypted": volume.get("Encrypted", False),
                    "KmsKeyId": kms_key_id.split("/")[-1] if kms_key_id != "None" else "None",
                    "MultiAttachEnabled": multi_attach_enabled,
                    "FastRestored": fast_restored,
                    "OutpostArn": outpost_arn if outpost_arn != "None" else "None",
                    "Tags": tags_str,
                    "Description": f"Unattached EBS volume ({age_days} days old)",
                })
        
        # Sort by age (oldest first)
        output_data.sort(key=lambda x: x["AgeDays"], reverse=True)
        
        # Calculate total potential savings
        total_monthly_cost = sum(
            float(vol["EstimatedMonthlyCost"].replace("$", ""))
            for vol in output_data
        )
        
        fields = {
            "1": "VolumeId",
            "2": "Name",
            "3": "Size",
            "4": "VolumeType",
            "5": "State",
            "6": "CreateTime",
            "7": "AgeDays",
            "8": "Iops",
            "9": "Throughput",
            "10": "SnapshotId",
            "11": "EstimatedMonthlyCost",
            "12": "AvailabilityZone",
            "13": "Encrypted",
            "14": "KmsKeyId",
            "15": "MultiAttachEnabled",
            "16": "FastRestored",
            "17": "OutpostArn",
            "18": "Tags",
            "19": "Description",
        }
        
        return {
            "id": 115,
            "name": "Unused EBS Volumes",
            "fields": fields,
            "headers": fields_to_headers(fields),
            "count": len(output_data),
            "total_monthly_cost": f"${total_monthly_cost:.2f}",
            "resource": output_data,
        }
        
    except Exception as e:
        logger.error(f"Error finding unused volumes: {e}")
        raise
