"""Network cost optimization tools for AWS resources."""

import logging
from datetime import datetime, timedelta
from typing import Any

from ..utils.helpers import fields_to_headers

logger = logging.getLogger(__name__)


def analyze_data_transfer_costs(
    session: Any, region_name: str = "us-east-1"
) -> dict[str, Any]:
    """Analyze data transfer costs using AWS Cost Explorer.
    
    Args:
        session: Boto3 session
        region_name: AWS region (Cost Explorer uses us-east-1)
    
    Returns:
        Dictionary with data transfer cost analysis
    """
    ce_client = session.client("ce", region_name="us-east-1")
    
    output_data = []
    
    logger.info("Analyzing data transfer costs")
    
    try:
        # Get costs for last 30 days
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        
        # Get data transfer costs by service
        response = ce_client.get_cost_and_usage(
            TimePeriod={"Start": start_date, "End": end_date},
            Granularity="MONTHLY",
            Metrics=["UnblendedCost"],
            GroupBy=[
                {"Type": "DIMENSION", "Key": "SERVICE"},
                {"Type": "DIMENSION", "Key": "USAGE_TYPE"}
            ],
            Filter={
                "Dimensions": {
                    "Key": "USAGE_TYPE_GROUP",
                    "Values": ["Data Transfer"]
                }
            }
        )
        
        for result in response.get("ResultsByTime", []):
            time_period = result.get("TimePeriod", {})
            groups = result.get("Groups", [])
            
            for group in groups:
                keys = group.get("Keys", [])
                service = keys[0] if len(keys) > 0 else "N/A"
                usage_type = keys[1] if len(keys) > 1 else "N/A"
                
                metrics = group.get("Metrics", {})
                cost = float(metrics.get("UnblendedCost", {}).get("Amount", "0"))
                
                if cost > 0:
                    # Determine transfer type
                    transfer_type = "Unknown"
                    if "Out" in usage_type or "DataTransfer-Out" in usage_type:
                        transfer_type = "Outbound"
                    elif "In" in usage_type or "DataTransfer-In" in usage_type:
                        transfer_type = "Inbound"
                    elif "Regional" in usage_type:
                        transfer_type = "Inter-Region"
                    elif "InterZone" in usage_type:
                        transfer_type = "Inter-AZ"
                    
                    # Determine recommendation
                    recommendation = ""
                    if transfer_type == "Outbound" and cost > 100:
                        recommendation = "Consider CloudFront or S3 Transfer Acceleration"
                    elif transfer_type == "Inter-Region" and cost > 50:
                        recommendation = "Consider VPC peering or PrivateLink"
                    elif transfer_type == "Inter-AZ" and cost > 50:
                        recommendation = "Review multi-AZ architecture necessity"
                    
                    output_data.append({
                        "Service": service,
                        "UsageType": usage_type,
                        "TransferType": transfer_type,
                        "MonthlyCost": f"${cost:.2f}",
                        "StartDate": time_period.get("Start", "N/A"),
                        "EndDate": time_period.get("End", "N/A"),
                        "Recommendation": recommendation if recommendation else "Monitor usage",
                    })
        
        total_monthly_cost = sum(
            float(item["MonthlyCost"].replace("$", ""))
            for item in output_data
        )
        
        fields = {
            "1": "Service",
            "2": "UsageType",
            "3": "TransferType",
            "4": "MonthlyCost",
            "5": "StartDate",
            "6": "EndDate",
            "7": "Recommendation",
        }
        
        return {
            "id": 307,
            "name": "Data Transfer Cost Analysis",
            "fields": fields,
            "headers": fields_to_headers(fields),
            "count": len(output_data),
            "total_monthly_cost": f"${total_monthly_cost:.2f}",
            "resource": output_data,
        }
        
    except Exception as e:
        logger.error(f"Error analyzing data transfer costs: {e}")
        raise


def get_nat_gateway_optimization_recommendations(
    session: Any, region_name: str
) -> dict[str, Any]:
    """Get recommendations for optimizing NAT Gateway costs.
    
    Args:
        session: Boto3 session
        region_name: AWS region name
    
    Returns:
        Dictionary with NAT Gateway optimization recommendations
    """
    ec2_client = session.client("ec2", region_name=region_name)
    cloudwatch_client = session.client("cloudwatch", region_name=region_name)
    
    output_data = []
    
    logger.info(f"Getting NAT Gateway optimization recommendations in {region_name}")
    
    try:
        # Get all NAT Gateways
        response = ec2_client.describe_nat_gateways()
        
        start_time = datetime.now() - timedelta(days=30)
        end_time = datetime.now()
        
        for nat_gateway in response["NatGateways"]:
            nat_gateway_id = nat_gateway["NatGatewayId"]
            state = nat_gateway["State"]
            subnet_id = nat_gateway["SubnetId"]
            vpc_id = nat_gateway["VpcId"]
            
            if state != "available":
                continue
            
            # Check data processed
            bytes_out_metric = cloudwatch_client.get_metric_statistics(
                Namespace="AWS/NATGateway",
                MetricName="BytesOutToDestination",
                Dimensions=[{"Name": "NatGatewayId", "Value": nat_gateway_id}],
                StartTime=start_time,
                EndTime=end_time,
                Period=86400,
                Statistics=["Sum"]
            )
            
            bytes_in_metric = cloudwatch_client.get_metric_statistics(
                Namespace="AWS/NATGateway",
                MetricName="BytesInFromSource",
                Dimensions=[{"Name": "NatGatewayId", "Value": nat_gateway_id}],
                StartTime=start_time,
                EndTime=end_time,
                Period=86400,
                Statistics=["Sum"]
            )
            
            total_bytes_out = 0
            total_bytes_in = 0
            
            if bytes_out_metric["Datapoints"]:
                total_bytes_out = sum(dp["Sum"] for dp in bytes_out_metric["Datapoints"])
            
            if bytes_in_metric["Datapoints"]:
                total_bytes_in = sum(dp["Sum"] for dp in bytes_in_metric["Datapoints"])
            
            total_gb_processed = (total_bytes_out + total_bytes_in) / (1024**3)
            
            # Calculate costs
            # NAT Gateway: $0.045/hour + $0.045/GB processed
            hourly_cost = 0.045
            monthly_hourly_cost = hourly_cost * 24 * 30
            data_processing_cost = total_gb_processed * 0.045
            total_monthly_cost = monthly_hourly_cost + data_processing_cost
            
            # Determine recommendation
            recommendation = ""
            potential_savings = 0.0
            
            if total_gb_processed < 10:
                recommendation = "Very low usage - consider removing or using VPC endpoints"
                potential_savings = total_monthly_cost * 0.9
            elif total_gb_processed < 100:
                recommendation = "Low usage - consider VPC endpoints for AWS services"
                potential_savings = data_processing_cost * 0.5
            else:
                recommendation = "Consider VPC endpoints to reduce data processing costs"
                potential_savings = data_processing_cost * 0.3
            
            # Get tags
            tags = {tag["Key"]: tag["Value"] for tag in nat_gateway.get("Tags", [])}
            
            output_data.append({
                "NatGatewayId": nat_gateway_id,
                "VpcId": vpc_id,
                "SubnetId": subnet_id,
                "State": state,
                "TotalGBProcessed": f"{total_gb_processed:.2f}",
                "MonthlyHourlyCost": f"${monthly_hourly_cost:.2f}",
                "DataProcessingCost": f"${data_processing_cost:.2f}",
                "TotalMonthlyCost": f"${total_monthly_cost:.2f}",
                "PotentialMonthlySavings": f"${potential_savings:.2f}",
                "Tags": str(tags),
                "Recommendation": recommendation,
            })
        
        total_monthly_cost = sum(
            float(item["TotalMonthlyCost"].replace("$", ""))
            for item in output_data
        )
        
        total_potential_savings = sum(
            float(item["PotentialMonthlySavings"].replace("$", ""))
            for item in output_data
        )
        
        fields = {
            "1": "NatGatewayId",
            "2": "VpcId",
            "3": "TotalGBProcessed",
            "4": "MonthlyHourlyCost",
            "5": "DataProcessingCost",
            "6": "TotalMonthlyCost",
            "7": "PotentialMonthlySavings",
            "8": "Recommendation",
            "9": "Tags",
        }
        
        return {
            "id": 308,
            "name": "NAT Gateway Optimization Recommendations",
            "fields": fields,
            "headers": fields_to_headers(fields),
            "count": len(output_data),
            "total_monthly_cost": f"${total_monthly_cost:.2f}",
            "total_potential_savings": f"${total_potential_savings:.2f}",
            "resource": output_data,
        }
        
    except Exception as e:
        logger.error(f"Error getting NAT Gateway optimization recommendations: {e}")
        raise
