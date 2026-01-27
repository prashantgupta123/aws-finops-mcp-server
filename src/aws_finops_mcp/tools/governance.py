"""Governance and tagging tools for AWS resources."""

import logging
from datetime import datetime, timedelta
from typing import Any
import json

from ..utils.helpers import fields_to_headers

logger = logging.getLogger(__name__)


def find_untagged_resources(
    session: Any, region_name: str, required_tags: list[str] | None = None
) -> dict[str, Any]:
    """Find resources without required tags.
    
    Args:
        session: Boto3 session
        region_name: AWS region name
        required_tags: List of required tag keys (default: ["Environment", "Owner", "CostCenter"])
    
    Returns:
        Dictionary with untagged resources
    """
    tagging_client = session.client("resourcegroupstaggingapi", region_name=region_name)
    
    if required_tags is None:
        required_tags = ["Environment", "Owner", "CostCenter"]
    
    output_data = []
    
    logger.info(f"Finding untagged resources in {region_name}")
    
    try:
        # Get all resources
        paginator = tagging_client.get_paginator("get_resources")
        
        for page in paginator.paginate():
            for resource in page.get("ResourceTagMappingList", []):
                resource_arn = resource["ResourceARN"]
                tags = {tag["Key"]: tag["Value"] for tag in resource.get("Tags", [])}
                
                # Check for missing required tags
                missing_tags = [tag for tag in required_tags if tag not in tags]
                
                if missing_tags:
                    # Extract resource type and ID from ARN
                    arn_parts = resource_arn.split(":")
                    service = arn_parts[2] if len(arn_parts) > 2 else "Unknown"
                    resource_type = arn_parts[5].split("/")[0] if len(arn_parts) > 5 else "Unknown"
                    resource_id = arn_parts[5].split("/")[-1] if len(arn_parts) > 5 else "Unknown"
                    
                    output_data.append({
                        "ResourceARN": resource_arn,
                        "Service": service,
                        "ResourceType": resource_type,
                        "ResourceId": resource_id,
                        "MissingTags": ", ".join(missing_tags),
                        "ExistingTags": str(tags),
                        "Recommendation": f"Add missing tags: {', '.join(missing_tags)}",
                    })
        
        fields = {
            "1": "ResourceARN",
            "2": "Service",
            "3": "ResourceType",
            "4": "ResourceId",
            "5": "MissingTags",
            "6": "ExistingTags",
            "7": "Recommendation",
        }
        
        return {
            "id": 701,
            "name": "Untagged Resources",
            "fields": fields,
            "headers": fields_to_headers(fields),
            "count": len(output_data),
            "resource": output_data,
        }
        
    except Exception as e:
        logger.error(f"Error finding untagged resources: {e}")
        raise


def analyze_tag_compliance(
    session: Any, region_name: str, required_tags: list[str] | None = None
) -> dict[str, Any]:
    """Analyze tag compliance across all resources.
    
    Args:
        session: Boto3 session
        region_name: AWS region name
        required_tags: List of required tag keys
    
    Returns:
        Dictionary with tag compliance analysis
    """
    tagging_client = session.client("resourcegroupstaggingapi", region_name=region_name)
    
    if required_tags is None:
        required_tags = ["Environment", "Owner", "CostCenter"]
    
    output_data = []
    
    logger.info(f"Analyzing tag compliance in {region_name}")
    
    try:
        # Get all resources
        paginator = tagging_client.get_paginator("get_resources")
        
        # Track compliance by service
        service_stats = {}
        
        for page in paginator.paginate():
            for resource in page.get("ResourceTagMappingList", []):
                resource_arn = resource["ResourceARN"]
                tags = {tag["Key"]: tag["Value"] for tag in resource.get("Tags", [])}
                
                # Extract service from ARN
                arn_parts = resource_arn.split(":")
                service = arn_parts[2] if len(arn_parts) > 2 else "Unknown"
                
                if service not in service_stats:
                    service_stats[service] = {
                        "total": 0,
                        "compliant": 0,
                        "non_compliant": 0
                    }
                
                service_stats[service]["total"] += 1
                
                # Check compliance
                missing_tags = [tag for tag in required_tags if tag not in tags]
                if not missing_tags:
                    service_stats[service]["compliant"] += 1
                else:
                    service_stats[service]["non_compliant"] += 1
        
        # Generate compliance report
        for service, stats in service_stats.items():
            compliance_rate = (stats["compliant"] / stats["total"] * 100) if stats["total"] > 0 else 0
            
            output_data.append({
                "Service": service,
                "TotalResources": stats["total"],
                "CompliantResources": stats["compliant"],
                "NonCompliantResources": stats["non_compliant"],
                "ComplianceRate": f"{compliance_rate:.2f}%",
                "RequiredTags": ", ".join(required_tags),
                "Recommendation": "Implement tag policies and automation" if compliance_rate < 80 else "Maintain current tagging practices",
            })
        
        # Sort by non-compliant count
        output_data.sort(key=lambda x: x["NonCompliantResources"], reverse=True)
        
        fields = {
            "1": "Service",
            "2": "TotalResources",
            "3": "CompliantResources",
            "4": "NonCompliantResources",
            "5": "ComplianceRate",
            "6": "RequiredTags",
            "7": "Recommendation",
        }
        
        return {
            "id": 702,
            "name": "Tag Compliance Analysis",
            "fields": fields,
            "headers": fields_to_headers(fields),
            "count": len(output_data),
            "resource": output_data,
        }
        
    except Exception as e:
        logger.error(f"Error analyzing tag compliance: {e}")
        raise


def generate_cost_allocation_report(
    session: Any, region_name: str = "us-east-1"
) -> dict[str, Any]:
    """Generate cost allocation report based on tags.
    
    Args:
        session: Boto3 session
        region_name: AWS region (Cost Explorer uses us-east-1)
    
    Returns:
        Dictionary with cost allocation report
    """
    ce_client = session.client("ce", region_name="us-east-1")
    
    output_data = []
    
    logger.info("Generating cost allocation report")
    
    try:
        # Get costs for last 30 days grouped by tags
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        
        # Common cost allocation tags
        tag_keys = ["Environment", "Owner", "CostCenter", "Project", "Application"]
        
        for tag_key in tag_keys:
            try:
                response = ce_client.get_cost_and_usage(
                    TimePeriod={"Start": start_date, "End": end_date},
                    Granularity="MONTHLY",
                    Metrics=["UnblendedCost"],
                    GroupBy=[{"Type": "TAG", "Key": tag_key}]
                )
                
                for result in response.get("ResultsByTime", []):
                    time_period = result.get("TimePeriod", {})
                    groups = result.get("Groups", [])
                    
                    for group in groups:
                        keys = group.get("Keys", [])
                        tag_value = keys[0].split("$")[-1] if keys else "Untagged"
                        
                        metrics = group.get("Metrics", {})
                        cost = float(metrics.get("UnblendedCost", {}).get("Amount", "0"))
                        
                        if cost > 0:
                            output_data.append({
                                "TagKey": tag_key,
                                "TagValue": tag_value,
                                "MonthlyCost": f"${cost:.2f}",
                                "StartDate": time_period.get("Start", "N/A"),
                                "EndDate": time_period.get("End", "N/A"),
                                "Recommendation": "Review and optimize costs" if cost > 1000 else "Monitor usage",
                            })
            except Exception as e:
                logger.warning(f"Could not get costs for tag {tag_key}: {e}")
                continue
        
        # Sort by cost
        output_data.sort(key=lambda x: float(x["MonthlyCost"].replace("$", "")), reverse=True)
        
        total_monthly_cost = sum(
            float(item["MonthlyCost"].replace("$", ""))
            for item in output_data
        )
        
        fields = {
            "1": "TagKey",
            "2": "TagValue",
            "3": "MonthlyCost",
            "4": "StartDate",
            "5": "EndDate",
            "6": "Recommendation",
        }
        
        return {
            "id": 703,
            "name": "Cost Allocation Report",
            "fields": fields,
            "headers": fields_to_headers(fields),
            "count": len(output_data),
            "total_monthly_cost": f"${total_monthly_cost:.2f}",
            "resource": output_data,
        }
        
    except Exception as e:
        logger.error(f"Error generating cost allocation report: {e}")
        raise
