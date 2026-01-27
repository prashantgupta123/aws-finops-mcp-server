"""Security and compliance tools for AWS resources."""

import logging
from datetime import datetime, timedelta
from typing import Any
import json

from ..utils.helpers import fields_to_headers

logger = logging.getLogger(__name__)


def find_unencrypted_ebs_volumes(
    session: Any, region_name: str
) -> dict[str, Any]:
    """Find EBS volumes without encryption enabled.
    
    Args:
        session: Boto3 session
        region_name: AWS region name
    
    Returns:
        Dictionary with unencrypted EBS volumes
    """
    ec2_client = session.client("ec2", region_name=region_name)
    
    output_data = []
    
    logger.info(f"Finding unencrypted EBS volumes in {region_name}")
    
    try:
        # Get all volumes that are not encrypted
        paginator = ec2_client.get_paginator("describe_volumes")
        
        for page in paginator.paginate(Filters=[{"Name": "encrypted", "Values": ["false"]}]):
            for volume in page["Volumes"]:
                volume_id = volume["VolumeId"]
                size = volume["Size"]
                volume_type = volume["VolumeType"]
                state = volume["State"]
                iops = volume.get("Iops", 0)
                
                # Get attachment info
                attachments = volume.get("Attachments", [])
                attached_to = "N/A"
                device = "N/A"
                if attachments:
                    attached_to = attachments[0].get("InstanceId", "N/A")
                    device = attachments[0].get("Device", "N/A")
                
                # Get tags
                tags = {tag["Key"]: tag["Value"] for tag in volume.get("Tags", [])}
                name = tags.get("Name", "N/A")
                
                # Calculate age
                create_time = volume.get("CreateTime")
                age_days = 0
                if create_time:
                    age_days = (datetime.now(create_time.tzinfo) - create_time).days
                
                availability_zone = volume.get("AvailabilityZone", "N/A")
                
                output_data.append({
                    "VolumeId": volume_id,
                    "VolumeName": name,
                    "Size": f"{size} GB",
                    "VolumeType": volume_type,
                    "State": state,
                    "IOPS": iops,
                    "AttachedTo": attached_to,
                    "Device": device,
                    "AvailabilityZone": availability_zone,
                    "AgeDays": age_days,
                    "Encrypted": "No",
                    "Tags": str(tags),
                    "Recommendation": "Enable encryption for data at rest security",
                    "RiskLevel": "High" if attached_to != "N/A" else "Medium",
                })
        
        fields = {
            "1": "VolumeId",
            "2": "VolumeName",
            "3": "Size",
            "4": "VolumeType",
            "5": "State",
            "6": "AttachedTo",
            "7": "Device",
            "8": "AvailabilityZone",
            "9": "AgeDays",
            "10": "RiskLevel",
            "11": "Recommendation",
            "12": "Tags",
        }
        
        return {
            "id": 601,
            "name": "Unencrypted EBS Volumes",
            "fields": fields,
            "headers": fields_to_headers(fields),
            "count": len(output_data),
            "resource": output_data,
        }
        
    except Exception as e:
        logger.error(f"Error finding unencrypted EBS volumes: {e}")
        raise


def find_unencrypted_s3_buckets(
    session: Any, region_name: str = "us-east-1"
) -> dict[str, Any]:
    """Find S3 buckets without default encryption enabled.
    
    Args:
        session: Boto3 session
        region_name: AWS region (S3 is global but uses us-east-1 endpoint)
    
    Returns:
        Dictionary with unencrypted S3 buckets
    """
    s3_client = session.client("s3", region_name="us-east-1")
    
    output_data = []
    
    logger.info("Finding unencrypted S3 buckets")
    
    try:
        # Get all buckets
        buckets_response = s3_client.list_buckets()
        
        for bucket in buckets_response.get("Buckets", []):
            bucket_name = bucket["Name"]
            
            try:
                # Check encryption configuration
                has_encryption = False
                encryption_type = "None"
                try:
                    encryption_response = s3_client.get_bucket_encryption(Bucket=bucket_name)
                    rules = encryption_response.get("ServerSideEncryptionConfiguration", {}).get("Rules", [])
                    if rules:
                        has_encryption = True
                        sse_algorithm = rules[0].get("ApplyServerSideEncryptionByDefault", {}).get("SSEAlgorithm", "Unknown")
                        encryption_type = sse_algorithm
                except s3_client.exceptions.ServerSideEncryptionConfigurationNotFoundError:
                    has_encryption = False
                
                if not has_encryption:
                    # Get bucket location
                    try:
                        location_response = s3_client.get_bucket_location(Bucket=bucket_name)
                        bucket_region = location_response.get("LocationConstraint") or "us-east-1"
                    except Exception:
                        bucket_region = "Unknown"
                    
                    # Get bucket size (approximate)
                    # Note: This requires CloudWatch metrics which may not be available
                    bucket_size = "Unknown"
                    
                    # Get tags
                    tags = {}
                    try:
                        tags_response = s3_client.get_bucket_tagging(Bucket=bucket_name)
                        tags = {tag["Key"]: tag["Value"] for tag in tags_response.get("TagSet", [])}
                    except Exception:
                        pass
                    
                    # Calculate age
                    creation_date = bucket.get("CreationDate")
                    age_days = 0
                    if creation_date:
                        age_days = (datetime.now(creation_date.tzinfo) - creation_date).days
                    
                    # Check versioning
                    versioning_status = "Disabled"
                    try:
                        versioning_response = s3_client.get_bucket_versioning(Bucket=bucket_name)
                        versioning_status = versioning_response.get("Status", "Disabled")
                    except Exception:
                        pass
                    
                    output_data.append({
                        "BucketName": bucket_name,
                        "Region": bucket_region,
                        "Encrypted": "No",
                        "EncryptionType": encryption_type,
                        "VersioningStatus": versioning_status,
                        "AgeDays": age_days,
                        "CreationDate": creation_date.strftime("%Y-%m-%d") if creation_date else "Unknown",
                        "Tags": str(tags),
                        "Recommendation": "Enable default encryption (AES256 or aws:kms)",
                        "RiskLevel": "High",
                    })
            except Exception as e:
                logger.warning(f"Could not check encryption for bucket {bucket_name}: {e}")
                continue
        
        fields = {
            "1": "BucketName",
            "2": "Region",
            "3": "Encrypted",
            "4": "EncryptionType",
            "5": "VersioningStatus",
            "6": "AgeDays",
            "7": "CreationDate",
            "8": "RiskLevel",
            "9": "Recommendation",
            "10": "Tags",
        }
        
        return {
            "id": 602,
            "name": "Unencrypted S3 Buckets",
            "fields": fields,
            "headers": fields_to_headers(fields),
            "count": len(output_data),
            "resource": output_data,
        }
        
    except Exception as e:
        logger.error(f"Error finding unencrypted S3 buckets: {e}")
        raise


def find_unencrypted_rds_instances(
    session: Any, region_name: str
) -> dict[str, Any]:
    """Find RDS instances without encryption enabled.
    
    Args:
        session: Boto3 session
        region_name: AWS region name
    
    Returns:
        Dictionary with unencrypted RDS instances
    """
    rds_client = session.client("rds", region_name=region_name)
    
    output_data = []
    
    logger.info(f"Finding unencrypted RDS instances in {region_name}")
    
    try:
        # Get all DB instances
        paginator = rds_client.get_paginator("describe_db_instances")
        
        for page in paginator.paginate():
            for db_instance in page["DBInstances"]:
                storage_encrypted = db_instance.get("StorageEncrypted", False)
                
                if not storage_encrypted:
                    db_instance_id = db_instance["DBInstanceIdentifier"]
                    db_instance_arn = db_instance["DBInstanceArn"]
                    engine = db_instance["Engine"]
                    engine_version = db_instance["EngineVersion"]
                    db_instance_class = db_instance["DBInstanceClass"]
                    db_instance_status = db_instance["DBInstanceStatus"]
                    multi_az = db_instance.get("MultiAZ", False)
                    publicly_accessible = db_instance.get("PubliclyAccessible", False)
                    allocated_storage = db_instance.get("AllocatedStorage", 0)
                    storage_type = db_instance.get("StorageType", "N/A")
                    
                    # Get tags
                    tags = {}
                    try:
                        tags_response = rds_client.list_tags_for_resource(ResourceName=db_instance_arn)
                        tags = {tag["Key"]: tag["Value"] for tag in tags_response.get("TagList", [])}
                    except Exception:
                        pass
                    
                    # Calculate age
                    instance_create_time = db_instance.get("InstanceCreateTime")
                    age_days = 0
                    if instance_create_time:
                        age_days = (datetime.now(instance_create_time.tzinfo) - instance_create_time).days
                    
                    # Determine risk level
                    risk_level = "Critical" if publicly_accessible else "High"
                    
                    output_data.append({
                        "DBInstanceIdentifier": db_instance_id,
                        "DBInstanceArn": db_instance_arn,
                        "Engine": engine,
                        "EngineVersion": engine_version,
                        "DBInstanceClass": db_instance_class,
                        "DBInstanceStatus": db_instance_status,
                        "StorageEncrypted": "No",
                        "MultiAZ": "Yes" if multi_az else "No",
                        "PubliclyAccessible": "Yes" if publicly_accessible else "No",
                        "AllocatedStorage": f"{allocated_storage} GB",
                        "StorageType": storage_type,
                        "AgeDays": age_days,
                        "RiskLevel": risk_level,
                        "Tags": str(tags),
                        "Recommendation": "Enable encryption at rest (requires snapshot and restore)",
                    })
        
        fields = {
            "1": "DBInstanceIdentifier",
            "2": "Engine",
            "3": "EngineVersion",
            "4": "DBInstanceClass",
            "5": "DBInstanceStatus",
            "6": "StorageEncrypted",
            "7": "MultiAZ",
            "8": "PubliclyAccessible",
            "9": "AllocatedStorage",
            "10": "AgeDays",
            "11": "RiskLevel",
            "12": "Recommendation",
            "13": "DBInstanceArn",
            "14": "Tags",
        }
        
        return {
            "id": 603,
            "name": "Unencrypted RDS Instances",
            "fields": fields,
            "headers": fields_to_headers(fields),
            "count": len(output_data),
            "resource": output_data,
        }
        
    except Exception as e:
        logger.error(f"Error finding unencrypted RDS instances: {e}")
        raise


def find_public_s3_buckets(
    session: Any, region_name: str = "us-east-1"
) -> dict[str, Any]:
    """Find S3 buckets with public access enabled.
    
    Args:
        session: Boto3 session
        region_name: AWS region (S3 is global but uses us-east-1 endpoint)
    
    Returns:
        Dictionary with public S3 buckets
    """
    s3_client = session.client("s3", region_name="us-east-1")
    
    output_data = []
    
    logger.info("Finding public S3 buckets")
    
    try:
        # Get all buckets
        buckets_response = s3_client.list_buckets()
        
        for bucket in buckets_response.get("Buckets", []):
            bucket_name = bucket["Name"]
            
            try:
                # Check public access block configuration
                is_public = False
                public_access_details = []
                
                try:
                    public_access_response = s3_client.get_public_access_block(Bucket=bucket_name)
                    config = public_access_response.get("PublicAccessBlockConfiguration", {})
                    
                    if not config.get("BlockPublicAcls", True):
                        is_public = True
                        public_access_details.append("Public ACLs allowed")
                    if not config.get("IgnorePublicAcls", True):
                        is_public = True
                        public_access_details.append("Public ACLs not ignored")
                    if not config.get("BlockPublicPolicy", True):
                        is_public = True
                        public_access_details.append("Public bucket policies allowed")
                    if not config.get("RestrictPublicBuckets", True):
                        is_public = True
                        public_access_details.append("Public bucket access not restricted")
                except s3_client.exceptions.NoSuchPublicAccessBlockConfiguration:
                    is_public = True
                    public_access_details.append("No public access block configured")
                
                if is_public:
                    # Get bucket location
                    try:
                        location_response = s3_client.get_bucket_location(Bucket=bucket_name)
                        bucket_region = location_response.get("LocationConstraint") or "us-east-1"
                    except Exception:
                        bucket_region = "Unknown"
                    
                    # Get tags
                    tags = {}
                    try:
                        tags_response = s3_client.get_bucket_tagging(Bucket=bucket_name)
                        tags = {tag["Key"]: tag["Value"] for tag in tags_response.get("TagSet", [])}
                    except Exception:
                        pass
                    
                    # Calculate age
                    creation_date = bucket.get("CreationDate")
                    age_days = 0
                    if creation_date:
                        age_days = (datetime.now(creation_date.tzinfo) - creation_date).days
                    
                    # Check if bucket policy exists
                    has_bucket_policy = False
                    try:
                        s3_client.get_bucket_policy(Bucket=bucket_name)
                        has_bucket_policy = True
                    except Exception:
                        pass
                    
                    output_data.append({
                        "BucketName": bucket_name,
                        "Region": bucket_region,
                        "PublicAccessDetails": ", ".join(public_access_details),
                        "HasBucketPolicy": "Yes" if has_bucket_policy else "No",
                        "AgeDays": age_days,
                        "CreationDate": creation_date.strftime("%Y-%m-%d") if creation_date else "Unknown",
                        "Tags": str(tags),
                        "Recommendation": "Enable S3 Block Public Access settings",
                        "RiskLevel": "Critical",
                    })
            except Exception as e:
                logger.warning(f"Could not check public access for bucket {bucket_name}: {e}")
                continue
        
        fields = {
            "1": "BucketName",
            "2": "Region",
            "3": "PublicAccessDetails",
            "4": "HasBucketPolicy",
            "5": "AgeDays",
            "6": "CreationDate",
            "7": "RiskLevel",
            "8": "Recommendation",
            "9": "Tags",
        }
        
        return {
            "id": 604,
            "name": "Public S3 Buckets",
            "fields": fields,
            "headers": fields_to_headers(fields),
            "count": len(output_data),
            "resource": output_data,
        }
        
    except Exception as e:
        logger.error(f"Error finding public S3 buckets: {e}")
        raise


def find_overly_permissive_security_groups(
    session: Any, region_name: str
) -> dict[str, Any]:
    """Find security groups with overly permissive rules (0.0.0.0/0 or ::/0).
    
    Args:
        session: Boto3 session
        region_name: AWS region name
    
    Returns:
        Dictionary with overly permissive security groups
    """
    ec2_client = session.client("ec2", region_name=region_name)
    
    output_data = []
    
    logger.info(f"Finding overly permissive security groups in {region_name}")
    
    try:
        # Get all security groups
        paginator = ec2_client.get_paginator("describe_security_groups")
        
        for page in paginator.paginate():
            for sg in page["SecurityGroups"]:
                sg_id = sg["GroupId"]
                sg_name = sg["GroupName"]
                vpc_id = sg.get("VpcId", "N/A")
                description = sg.get("Description", "N/A")
                
                # Check for overly permissive inbound rules
                permissive_rules = []
                for rule in sg.get("IpPermissions", []):
                    from_port = rule.get("FromPort", "All")
                    to_port = rule.get("ToPort", "All")
                    ip_protocol = rule.get("IpProtocol", "All")
                    
                    # Check for 0.0.0.0/0 or ::/0
                    for ip_range in rule.get("IpRanges", []):
                        if ip_range.get("CidrIp") == "0.0.0.0/0":
                            permissive_rules.append(f"{ip_protocol}:{from_port}-{to_port} from 0.0.0.0/0")
                    
                    for ipv6_range in rule.get("Ipv6Ranges", []):
                        if ipv6_range.get("CidrIpv6") == "::/0":
                            permissive_rules.append(f"{ip_protocol}:{from_port}-{to_port} from ::/0")
                
                if permissive_rules:
                    # Get tags
                    tags = {tag["Key"]: tag["Value"] for tag in sg.get("Tags", [])}
                    
                    # Determine risk level based on ports
                    risk_level = "Medium"
                    for rule in permissive_rules:
                        if any(port in rule for port in ["22", "3389", "1433", "3306", "5432"]):
                            risk_level = "Critical"
                            break
                        elif any(port in rule for port in ["80", "443", "8080"]):
                            risk_level = "High"
                    
                    # Count associated resources
                    # Note: This would require additional API calls to check ENIs
                    associated_resources = "Unknown"
                    
                    output_data.append({
                        "SecurityGroupId": sg_id,
                        "SecurityGroupName": sg_name,
                        "VpcId": vpc_id,
                        "Description": description,
                        "PermissiveRules": "; ".join(permissive_rules),
                        "RuleCount": len(permissive_rules),
                        "RiskLevel": risk_level,
                        "Tags": str(tags),
                        "Recommendation": "Restrict inbound rules to specific IP ranges",
                    })
        
        fields = {
            "1": "SecurityGroupId",
            "2": "SecurityGroupName",
            "3": "VpcId",
            "4": "Description",
            "5": "PermissiveRules",
            "6": "RuleCount",
            "7": "RiskLevel",
            "8": "Recommendation",
            "9": "Tags",
        }
        
        return {
            "id": 605,
            "name": "Overly Permissive Security Groups",
            "fields": fields,
            "headers": fields_to_headers(fields),
            "count": len(output_data),
            "resource": output_data,
        }
        
    except Exception as e:
        logger.error(f"Error finding overly permissive security groups: {e}")
        raise
