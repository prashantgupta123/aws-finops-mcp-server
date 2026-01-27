"""Container upgrade recommendation tools for AWS resources."""

import logging
from datetime import datetime, timedelta
from typing import Any

from ..utils.helpers import fields_to_headers

logger = logging.getLogger(__name__)


def find_outdated_eks_cluster_versions(
    session: Any, region_name: str
) -> dict[str, Any]:
    """Find EKS clusters not running the latest Kubernetes version.
    
    Args:
        session: Boto3 session
        region_name: AWS region name
    
    Returns:
        Dictionary with outdated EKS clusters
    """
    eks_client = session.client("eks", region_name=region_name)
    
    output_data = []
    
    logger.info(f"Finding outdated EKS cluster versions in {region_name}")
    
    try:
        # Get all EKS clusters
        clusters_response = eks_client.list_clusters()
        
        # Latest supported versions (as of 2024)
        latest_version = "1.29"
        supported_versions = ["1.29", "1.28", "1.27", "1.26"]
        
        for cluster_name in clusters_response.get("clusters", []):
            try:
                # Get cluster details
                cluster_response = eks_client.describe_cluster(name=cluster_name)
                cluster = cluster_response["cluster"]
                
                cluster_arn = cluster["arn"]
                version = cluster["version"]
                status = cluster["status"]
                platform_version = cluster.get("platformVersion", "N/A")
                
                # Check if version is outdated
                is_outdated = version not in supported_versions[:2]  # Not in latest 2 versions
                
                if is_outdated:
                    # Get creation time
                    created_at = cluster.get("createdAt")
                    age_days = 0
                    if created_at:
                        age_days = (datetime.now(created_at.tzinfo) - created_at).days
                    
                    # Get tags
                    tags = cluster.get("tags", {})
                    
                    # Get node groups count
                    nodegroups_response = eks_client.list_nodegroups(clusterName=cluster_name)
                    nodegroup_count = len(nodegroups_response.get("nodegroups", []))
                    
                    output_data.append({
                        "ClusterName": cluster_name,
                        "ClusterArn": cluster_arn,
                        "CurrentVersion": version,
                        "LatestVersion": latest_version,
                        "Status": status,
                        "PlatformVersion": platform_version,
                        "NodeGroupCount": nodegroup_count,
                        "AgeDays": age_days,
                        "Tags": str(tags),
                        "Recommendation": f"Upgrade from {version} to {latest_version}",
                        "RiskLevel": "High" if version not in supported_versions else "Medium",
                    })
            except Exception as e:
                logger.warning(f"Could not check cluster {cluster_name}: {e}")
                continue
        
        fields = {
            "1": "ClusterName",
            "2": "CurrentVersion",
            "3": "LatestVersion",
            "4": "Status",
            "5": "PlatformVersion",
            "6": "NodeGroupCount",
            "7": "AgeDays",
            "8": "RiskLevel",
            "9": "Recommendation",
            "10": "ClusterArn",
            "11": "Tags",
        }
        
        return {
            "id": 407,
            "name": "Outdated EKS Cluster Versions",
            "fields": fields,
            "headers": fields_to_headers(fields),
            "count": len(output_data),
            "resource": output_data,
        }
        
    except Exception as e:
        logger.error(f"Error finding outdated EKS cluster versions: {e}")
        raise
