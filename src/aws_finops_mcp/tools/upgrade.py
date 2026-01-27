"""Upgrade recommendation tools."""

import logging
from datetime import datetime, timedelta
from typing import Any

from ..utils.helpers import fields_to_headers

logger = logging.getLogger(__name__)


def find_asgs_with_old_amis(
    session: Any, region_name: str, period: int, max_results: int = 100
) -> dict[str, Any]:
    """Find Auto Scaling Groups using AMIs older than the specified period."""
    ec2_client = session.client("ec2", region_name=region_name)
    asg_client = session.client("autoscaling", region_name=region_name)
    
    cutoff_date = datetime.now() - timedelta(days=period)
    old_ami_asgs = []
    
    # Get all ASGs
    response = asg_client.describe_auto_scaling_groups(MaxRecords=max_results)
    
    for asg in response["AutoScalingGroups"]:
        asg_name = asg["AutoScalingGroupName"]
        ami_id = None
        
        # Get AMI from launch template
        if "LaunchTemplate" in asg:
            lt_id = asg["LaunchTemplate"]["LaunchTemplateId"]
            lt_version = asg["LaunchTemplate"]["Version"]
            
            try:
                lt_response = ec2_client.describe_launch_template_versions(
                    LaunchTemplateId=lt_id, Versions=[lt_version]
                )
                
                for version in lt_response["LaunchTemplateVersions"]:
                    if "ImageId" in version["LaunchTemplateData"]:
                        ami_id = version["LaunchTemplateData"]["ImageId"]
                        break
            except Exception as e:
                logger.warning(f"Error getting launch template for ASG {asg_name}: {e}")
                continue
        
        # Get AMI from mixed instances policy
        elif "MixedInstancesPolicy" in asg:
            lt_spec = asg["MixedInstancesPolicy"]["LaunchTemplate"]["LaunchTemplateSpecification"]
            lt_id = lt_spec["LaunchTemplateId"]
            lt_version = lt_spec["Version"]
            
            try:
                lt_response = ec2_client.describe_launch_template_versions(
                    LaunchTemplateId=lt_id, Versions=[lt_version]
                )
                
                for version in lt_response["LaunchTemplateVersions"]:
                    if "ImageId" in version["LaunchTemplateData"]:
                        ami_id = version["LaunchTemplateData"]["ImageId"]
                        break
            except Exception as e:
                logger.warning(f"Error getting launch template for ASG {asg_name}: {e}")
                continue
        
        if not ami_id:
            continue
        
        # Get AMI details
        try:
            ami_response = ec2_client.describe_images(ImageIds=[ami_id])
            
            if not ami_response["Images"]:
                continue
            
            ami = ami_response["Images"][0]
            creation_date = datetime.strptime(ami["CreationDate"], "%Y-%m-%dT%H:%M:%S.%fZ")
            
            # Check if AMI is older than cutoff
            if creation_date < cutoff_date:
                age_days = (datetime.now() - creation_date).days
                
                old_ami_asgs.append({
                    "AutoScalingGroupName": asg_name,
                    "AMIId": ami_id,
                    "AMIName": ami.get("Name", ""),
                    "AMICreationDate": ami["CreationDate"],
                    "AMIAge": f"{age_days} days",
                    "Platform": ami.get("Platform", "Linux/UNIX"),
                    "MinSize": asg.get("MinSize", 0),
                    "MaxSize": asg.get("MaxSize", 0),
                    "DesiredCapacity": asg.get("DesiredCapacity", 0),
                    "Description": f"ASG using AMI that is {age_days} days old (threshold: {period} days)",
                })
        except Exception as e:
            logger.warning(f"Error getting AMI details for {ami_id}: {e}")
            continue
    
    fields = {
        "1": "AutoScalingGroupName",
        "2": "AMIId",
        "3": "AMIName",
        "4": "AMICreationDate",
        "5": "AMIAge",
        "6": "Platform",
        "7": "MinSize",
        "8": "MaxSize",
        "9": "DesiredCapacity",
        "10": "Description",
    }
    
    return {
        "id": 113,
        "name": "ASGs with Old AMIs",
        "fields": fields,
        "headers": fields_to_headers(fields),
        "count": len(old_ami_asgs),
        "resource": old_ami_asgs,
    }
