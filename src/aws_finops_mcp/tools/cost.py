"""Cost optimization tools using AWS Cost Optimization Hub."""

import logging
from typing import Any

from ..utils.helpers import fields_to_headers

logger = logging.getLogger(__name__)


# Resource type configuration with IDs and names
RESOURCE_TYPES_CONFIG = {
    "Ec2Instance": {"id": 201, "name": "Cost_Ec2Instance"},
    "LambdaFunction": {"id": 202, "name": "Cost_LambdaFunction"},
    "EbsVolume": {"id": 203, "name": "Cost_EbsVolume"},
    "EcsService": {"id": 204, "name": "Cost_EcsService"},
    "Ec2AutoScalingGroup": {"id": 205, "name": "Cost_Ec2AutoScalingGroup"},
    "Ec2InstanceSavingsPlans": {"id": 206, "name": "Cost_Ec2InstanceSavingsPlans"},
    "ComputeSavingsPlans": {"id": 207, "name": "Cost_ComputeSavingsPlans"},
    "SageMakerSavingsPlans": {"id": 208, "name": "Cost_SageMakerSavingsPlans"},
    "Ec2ReservedInstances": {"id": 209, "name": "Cost_Ec2ReservedInstances"},
    "RdsReservedInstances": {"id": 210, "name": "Cost_RdsReservedInstances"},
    "OpenSearchReservedInstances": {"id": 211, "name": "Cost_OpenSearchReservedInstances"},
    "RedshiftReservedInstances": {"id": 212, "name": "Cost_RedshiftReservedInstances"},
    "ElastiCacheReservedInstances": {"id": 213, "name": "Cost_ElastiCacheReservedInstances"},
    "RdsDbInstanceStorage": {"id": 214, "name": "Cost_RdsDbInstanceStorage"},
    "RdsDbInstance": {"id": 215, "name": "Cost_RdsDbInstance"},
    "AuroraDbClusterStorage": {"id": 216, "name": "Cost_AuroraDbClusterStorage"},
    "DynamoDbReservedCapacity": {"id": 217, "name": "Cost_DynamoDbReservedCapacity"},
    "MemoryDbReservedInstances": {"id": 218, "name": "Cost_MemoryDbReservedInstances"},
    "NatGateway": {"id": 219, "name": "Cost_NatGateway"},
}


def get_resource_fields() -> dict[str, str]:
    """Get standardized fields for all cost optimization resource types."""
    return {
        "1": "RecommendationId",
        "2": "AccountId",
        "3": "Region",
        "4": "ResourceId",
        "5": "ResourceArn",
        "6": "CurrentResourceType",
        "7": "RecommendedResourceType",
        "8": "EstimatedMonthlySavings",
        "9": "EstimatedSavingsPercentage",
        "10": "EstimatedMonthlyCost",
        "11": "CurrencyCode",
        "12": "ImplementationEffort",
        "13": "RestartNeeded",
        "14": "ActionType",
        "15": "RollbackPossible",
        "16": "CurrentResourceSummary",
        "17": "RecommendedResourceSummary",
        "18": "LastRefreshTimestamp",
        "19": "RecommendationLookbackPeriodInDays",
        "20": "Source",
        "21": "Description",
    }


def list_recommendations(
    client: Any, max_results: int = 50, region_filter: str | None = None
) -> dict[str, Any]:
    """Retrieve detailed recommendations from Cost Optimization Hub."""
    all_items = []
    next_token = None
    
    while True:
        params = {
            "maxResults": max_results,
            "includeAllRecommendations": True,
            "orderBy": {"dimension": "ResourceType", "order": "Asc"},
        }
        
        # Add region filter if specified
        if region_filter:
            params["filter"] = {"regions": [region_filter]}
        
        if next_token:
            params["nextToken"] = next_token
        
        try:
            response = client.list_recommendations(**params)
            all_items.extend(response.get("items", []))
            
            next_token = response.get("nextToken")
            if not next_token:
                break
        except Exception as e:
            logger.error(f"Error listing recommendations: {e}")
            break
    
    return {"items": all_items}


def process_recommendations_by_resource_type(
    recommendations: dict[str, Any], resource_type: str
) -> list[dict[str, Any]]:
    """Process recommendations for a specific resource type."""
    filtered_recommendations = []
    
    for item in recommendations.get("items", []):
        if item.get("currentResourceType") == resource_type:
            recommendation = {
                "RecommendationId": item.get("recommendationId", ""),
                "AccountId": item.get("accountId", ""),
                "Region": item.get("region", ""),
                "ResourceId": item.get("resourceId", ""),
                "ResourceArn": item.get("resourceArn", ""),
                "CurrentResourceType": item.get("currentResourceType", ""),
                "RecommendedResourceType": item.get("recommendedResourceType", ""),
                "EstimatedMonthlySavings": item.get("estimatedMonthlySavings", 0),
                "EstimatedSavingsPercentage": item.get("estimatedSavingsPercentage", 0),
                "EstimatedMonthlyCost": item.get("estimatedMonthlyCost", 0),
                "CurrencyCode": item.get("currencyCode", "USD"),
                "ImplementationEffort": item.get("implementationEffort", ""),
                "RestartNeeded": item.get("restartNeeded", False),
                "ActionType": item.get("actionType", ""),
                "RollbackPossible": item.get("rollbackPossible", False),
                "CurrentResourceSummary": item.get("currentResourceSummary", ""),
                "RecommendedResourceSummary": item.get("recommendedResourceSummary", ""),
                "LastRefreshTimestamp": str(item.get("lastRefreshTimestamp", "")),
                "RecommendationLookbackPeriodInDays": item.get(
                    "recommendationLookbackPeriodInDays", 0
                ),
                "Source": item.get("source", ""),
                "Description": f"Cost optimization: {item.get('actionType', '')} for {resource_type}",
            }
            filtered_recommendations.append(recommendation)
    
    return filtered_recommendations


def get_cost_optimization_recommendations(
    session: Any, region_name: str, resource_type: str | None = None
) -> list[dict[str, Any]] | dict[str, Any]:
    """Get cost optimization recommendations from AWS Cost Optimization Hub.
    
    Args:
        session: Boto3 session
        region_name: AWS region for filtering (optional)
        resource_type: Specific resource type to filter (optional)
        
    Returns:
        List of resource objects (one per resource type) or single resource object
    """
    try:
        # Cost Optimization Hub is only available in us-east-1
        client = session.client("cost-optimization-hub", region_name="us-east-1")
        
        # Get all recommendations
        recommendations = list_recommendations(
            client, max_results=50, region_filter=region_name
        )
        
        fields = get_resource_fields()
        
        # If specific resource type requested, return only that
        if resource_type and resource_type in RESOURCE_TYPES_CONFIG:
            config = RESOURCE_TYPES_CONFIG[resource_type]
            filtered_recommendations = process_recommendations_by_resource_type(
                recommendations, resource_type
            )
            
            return {
                "id": config["id"],
                "name": config["name"],
                "fields": fields,
                "headers": fields_to_headers(fields),
                "count": len(filtered_recommendations),
                "resource": filtered_recommendations,
            }
        
        # Otherwise, return all resource types
        results = []
        for resource_type, config in RESOURCE_TYPES_CONFIG.items():
            filtered_recommendations = process_recommendations_by_resource_type(
                recommendations, resource_type
            )
            
            resource_obj = {
                "id": config["id"],
                "name": config["name"],
                "fields": fields,
                "headers": fields_to_headers(fields),
                "count": len(filtered_recommendations),
                "resource": filtered_recommendations,
            }
            
            results.append(resource_obj)
        
        total_recommendations = sum(len(result["resource"]) for result in results)
        logger.info(f"AWS Cost Optimization completed: {total_recommendations} recommendations")
        
        return results
        
    except Exception as e:
        logger.error(f"Error in cost optimization: {e}")
        raise
