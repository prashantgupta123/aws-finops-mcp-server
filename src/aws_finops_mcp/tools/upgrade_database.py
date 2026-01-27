"""Database upgrade recommendation tools for AWS resources."""

import logging
from datetime import datetime, timedelta
from typing import Any

from ..utils.helpers import fields_to_headers

logger = logging.getLogger(__name__)


def find_outdated_rds_engine_versions(
    session: Any, region_name: str
) -> dict[str, Any]:
    """Find RDS instances not running the latest engine version.
    
    Args:
        session: Boto3 session
        region_name: AWS region name
    
    Returns:
        Dictionary with outdated RDS instances
    """
    rds_client = session.client("rds", region_name=region_name)
    
    output_data = []
    
    logger.info(f"Finding outdated RDS engine versions in {region_name}")
    
    try:
        # Get all DB instances
        paginator = rds_client.get_paginator("describe_db_instances")
        
        # Cache for latest engine versions
        latest_versions = {}
        
        for page in paginator.paginate():
            for db_instance in page["DBInstances"]:
                db_instance_id = db_instance["DBInstanceIdentifier"]
                db_instance_arn = db_instance["DBInstanceArn"]
                engine = db_instance["Engine"]
                engine_version = db_instance["EngineVersion"]
                db_instance_class = db_instance["DBInstanceClass"]
                db_instance_status = db_instance["DBInstanceStatus"]
                multi_az = db_instance.get("MultiAZ", False)
                storage_type = db_instance.get("StorageType", "N/A")
                allocated_storage = db_instance.get("AllocatedStorage", 0)
                
                # Get latest engine version if not cached
                if engine not in latest_versions:
                    try:
                        engine_versions_response = rds_client.describe_db_engine_versions(
                            Engine=engine,
                            DefaultOnly=True
                        )
                        if engine_versions_response["DBEngineVersions"]:
                            latest_versions[engine] = engine_versions_response["DBEngineVersions"][0]["EngineVersion"]
                        else:
                            # If no default, get all and pick latest
                            all_versions_response = rds_client.describe_db_engine_versions(
                                Engine=engine
                            )
                            if all_versions_response["DBEngineVersions"]:
                                # Sort versions and get latest
                                versions = [v["EngineVersion"] for v in all_versions_response["DBEngineVersions"]]
                                latest_versions[engine] = sorted(versions, reverse=True)[0]
                            else:
                                latest_versions[engine] = engine_version
                    except Exception as e:
                        logger.warning(f"Could not get latest version for {engine}: {e}")
                        latest_versions[engine] = engine_version
                
                latest_version = latest_versions.get(engine, engine_version)
                is_outdated = engine_version != latest_version
                
                if is_outdated:
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
                    
                    output_data.append({
                        "DBInstanceIdentifier": db_instance_id,
                        "DBInstanceArn": db_instance_arn,
                        "Engine": engine,
                        "CurrentVersion": engine_version,
                        "LatestVersion": latest_version,
                        "DBInstanceClass": db_instance_class,
                        "DBInstanceStatus": db_instance_status,
                        "MultiAZ": "Yes" if multi_az else "No",
                        "StorageType": storage_type,
                        "AllocatedStorage": f"{allocated_storage} GB",
                        "AgeDays": age_days,
                        "Tags": str(tags),
                        "Recommendation": f"Upgrade from {engine_version} to {latest_version}",
                    })
        
        fields = {
            "1": "DBInstanceIdentifier",
            "2": "Engine",
            "3": "CurrentVersion",
            "4": "LatestVersion",
            "5": "DBInstanceClass",
            "6": "DBInstanceStatus",
            "7": "MultiAZ",
            "8": "StorageType",
            "9": "AllocatedStorage",
            "10": "AgeDays",
            "11": "Recommendation",
            "12": "DBInstanceArn",
            "13": "Tags",
        }
        
        return {
            "id": 401,
            "name": "Outdated RDS Engine Versions",
            "fields": fields,
            "headers": fields_to_headers(fields),
            "count": len(output_data),
            "resource": output_data,
        }
        
    except Exception as e:
        logger.error(f"Error finding outdated RDS engine versions: {e}")
        raise


def find_outdated_elasticache_engine_versions(
    session: Any, region_name: str
) -> dict[str, Any]:
    """Find ElastiCache clusters not running the latest engine version.
    
    Args:
        session: Boto3 session
        region_name: AWS region name
    
    Returns:
        Dictionary with outdated ElastiCache clusters
    """
    elasticache_client = session.client("elasticache", region_name=region_name)
    
    output_data = []
    
    logger.info(f"Finding outdated ElastiCache engine versions in {region_name}")
    
    try:
        # Get all cache clusters
        paginator = elasticache_client.get_paginator("describe_cache_clusters")
        
        # Cache for latest engine versions
        latest_versions = {}
        
        for page in paginator.paginate():
            for cluster in page["CacheClusters"]:
                cluster_id = cluster["CacheClusterId"]
                cluster_arn = cluster["ARN"]
                engine = cluster["Engine"]
                engine_version = cluster["EngineVersion"]
                cache_node_type = cluster["CacheNodeType"]
                cluster_status = cluster["CacheClusterStatus"]
                num_cache_nodes = cluster.get("NumCacheNodes", 0)
                
                # Get latest engine version if not cached
                if engine not in latest_versions:
                    try:
                        engine_versions_response = elasticache_client.describe_cache_engine_versions(
                            Engine=engine,
                            DefaultOnly=True
                        )
                        if engine_versions_response["CacheEngineVersions"]:
                            latest_versions[engine] = engine_versions_response["CacheEngineVersions"][0]["EngineVersion"]
                        else:
                            # Get all versions and pick latest
                            all_versions_response = elasticache_client.describe_cache_engine_versions(
                                Engine=engine
                            )
                            if all_versions_response["CacheEngineVersions"]:
                                versions = [v["EngineVersion"] for v in all_versions_response["CacheEngineVersions"]]
                                latest_versions[engine] = sorted(versions, reverse=True)[0]
                            else:
                                latest_versions[engine] = engine_version
                    except Exception as e:
                        logger.warning(f"Could not get latest version for {engine}: {e}")
                        latest_versions[engine] = engine_version
                
                latest_version = latest_versions.get(engine, engine_version)
                is_outdated = engine_version != latest_version
                
                if is_outdated:
                    # Get tags
                    tags = {}
                    try:
                        tags_response = elasticache_client.list_tags_for_resource(ResourceName=cluster_arn)
                        tags = {tag["Key"]: tag["Value"] for tag in tags_response.get("TagList", [])}
                    except Exception:
                        pass
                    
                    # Calculate age
                    cluster_create_time = cluster.get("CacheClusterCreateTime")
                    age_days = 0
                    if cluster_create_time:
                        age_days = (datetime.now(cluster_create_time.tzinfo) - cluster_create_time).days
                    
                    output_data.append({
                        "CacheClusterId": cluster_id,
                        "CacheClusterArn": cluster_arn,
                        "Engine": engine,
                        "CurrentVersion": engine_version,
                        "LatestVersion": latest_version,
                        "CacheNodeType": cache_node_type,
                        "CacheClusterStatus": cluster_status,
                        "NumCacheNodes": num_cache_nodes,
                        "AgeDays": age_days,
                        "Tags": str(tags),
                        "Recommendation": f"Upgrade from {engine_version} to {latest_version}",
                    })
        
        fields = {
            "1": "CacheClusterId",
            "2": "Engine",
            "3": "CurrentVersion",
            "4": "LatestVersion",
            "5": "CacheNodeType",
            "6": "CacheClusterStatus",
            "7": "NumCacheNodes",
            "8": "AgeDays",
            "9": "Recommendation",
            "10": "CacheClusterArn",
            "11": "Tags",
        }
        
        return {
            "id": 402,
            "name": "Outdated ElastiCache Engine Versions",
            "fields": fields,
            "headers": fields_to_headers(fields),
            "count": len(output_data),
            "resource": output_data,
        }
        
    except Exception as e:
        logger.error(f"Error finding outdated ElastiCache engine versions: {e}")
        raise
