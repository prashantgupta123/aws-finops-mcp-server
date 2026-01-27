"""Cost savings and optimization recommendation tools for AWS resources."""

import logging
from datetime import datetime, timedelta
from typing import Any

from ..utils.helpers import fields_to_headers

logger = logging.getLogger(__name__)


def get_savings_plans_recommendations(
    session: Any, region_name: str = "us-east-1"
) -> dict[str, Any]:
    """Get Savings Plans recommendations from AWS Cost Explorer.
    
    Args:
        session: Boto3 session
        region_name: AWS region (Cost Explorer always uses us-east-1)
    
    Returns:
        Dictionary with Savings Plans recommendations
    """
    ce_client = session.client("ce", region_name="us-east-1")
    
    output_data = []
    
    logger.info("Getting Savings Plans recommendations")
    
    try:
        # Get recommendations for different Savings Plans types
        for sp_type in ["COMPUTE_SP", "EC2_INSTANCE_SP", "SAGEMAKER_SP"]:
            try:
                response = ce_client.get_savings_plans_purchase_recommendation(
                    SavingsPlansType=sp_type,
                    LookbackPeriodInDays="SIXTY_DAYS",
                    TermInYears="ONE_YEAR",
                    PaymentOption="NO_UPFRONT"
                )
                
                metadata = response.get("Metadata", {})
                recommendations = response.get("SavingsPlansPurchaseRecommendation", {})
                
                for detail in recommendations.get("SavingsPlansPurchaseRecommendationDetails", []):
                    savings_plans_details = detail.get("SavingsPlansDetails", {})
                    
                    hourly_commitment = detail.get("HourlyCommitmentToPurchase", "0")
                    upfront_cost = detail.get("UpfrontCost", "0")
                    estimated_monthly_savings = detail.get("EstimatedMonthlySavings", "0")
                    estimated_savings_percentage = detail.get("EstimatedSavingsPercentage", "0")
                    estimated_roi = detail.get("EstimatedROI", "0")
                    
                    output_data.append({
                        "SavingsPlansType": sp_type,
                        "Region": savings_plans_details.get("Region", "N/A"),
                        "InstanceFamily": savings_plans_details.get("InstanceFamily", "N/A"),
                        "OfferingId": savings_plans_details.get("OfferingId", "N/A"),
                        "HourlyCommitment": f"${float(hourly_commitment):.4f}",
                        "UpfrontCost": f"${float(upfront_cost):.2f}",
                        "EstimatedMonthlySavings": f"${float(estimated_monthly_savings):.2f}",
                        "EstimatedSavingsPercentage": f"{float(estimated_savings_percentage):.2f}%",
                        "EstimatedROI": f"{float(estimated_roi):.2f}%",
                        "CurrentAverageHourlyOnDemandSpend": detail.get("CurrentAverageHourlyOnDemandSpend", "0"),
                        "CurrentMaximumHourlyOnDemandSpend": detail.get("CurrentMaximumHourlyOnDemandSpend", "0"),
                        "CurrentMinimumHourlyOnDemandSpend": detail.get("CurrentMinimumHourlyOnDemandSpend", "0"),
                    })
            except Exception as e:
                logger.warning(f"Could not get recommendations for {sp_type}: {e}")
                continue
        
        total_monthly_savings = sum(
            float(item["EstimatedMonthlySavings"].replace("$", "").replace(",", ""))
            for item in output_data
        )
        
        fields = {
            "1": "SavingsPlansType",
            "2": "Region",
            "3": "InstanceFamily",
            "4": "HourlyCommitment",
            "5": "UpfrontCost",
            "6": "EstimatedMonthlySavings",
            "7": "EstimatedSavingsPercentage",
            "8": "EstimatedROI",
            "9": "CurrentAverageHourlyOnDemandSpend",
            "10": "OfferingId",
        }
        
        return {
            "id": 302,
            "name": "Savings Plans Recommendations",
            "fields": fields,
            "headers": fields_to_headers(fields),
            "count": len(output_data),
            "total_monthly_savings": f"${total_monthly_savings:.2f}",
            "resource": output_data,
        }
        
    except Exception as e:
        logger.error(f"Error getting Savings Plans recommendations: {e}")
        raise


def get_reserved_instance_recommendations(
    session: Any, region_name: str = "us-east-1", service: str = "EC2"
) -> dict[str, Any]:
    """Get Reserved Instance purchase recommendations from AWS Cost Explorer.
    
    Args:
        session: Boto3 session
        region_name: AWS region (Cost Explorer always uses us-east-1)
        service: AWS service (EC2, RDS, ElastiCache, Redshift, OpenSearch)
    
    Returns:
        Dictionary with Reserved Instance recommendations
    """
    ce_client = session.client("ce", region_name="us-east-1")
    
    output_data = []
    
    logger.info(f"Getting Reserved Instance recommendations for {service}")
    
    try:
        response = ce_client.get_reservation_purchase_recommendation(
            Service=service.upper(),
            LookbackPeriodInDays="SIXTY_DAYS",
            TermInYears="ONE_YEAR",
            PaymentOption="NO_UPFRONT"
        )
        
        metadata = response.get("Metadata", {})
        recommendations = response.get("Recommendations", [])
        
        for rec in recommendations:
            rec_details = rec.get("RecommendationDetails", {})
            instance_details = rec_details.get("InstanceDetails", {})
            
            # Extract instance details based on service type
            if service.upper() == "EC2":
                ec2_details = instance_details.get("EC2InstanceDetails", {})
                instance_type = ec2_details.get("InstanceType", "N/A")
                platform = ec2_details.get("Platform", "N/A")
                region = ec2_details.get("Region", "N/A")
                tenancy = ec2_details.get("Tenancy", "N/A")
            elif service.upper() == "RDS":
                rds_details = instance_details.get("RDSInstanceDetails", {})
                instance_type = rds_details.get("InstanceType", "N/A")
                platform = rds_details.get("DatabaseEngine", "N/A")
                region = rds_details.get("Region", "N/A")
                tenancy = "N/A"
            else:
                instance_type = "N/A"
                platform = "N/A"
                region = "N/A"
                tenancy = "N/A"
            
            rec_summary = rec.get("RecommendationSummary", {})
            
            output_data.append({
                "Service": service.upper(),
                "InstanceType": instance_type,
                "Platform": platform,
                "Region": region,
                "Tenancy": tenancy,
                "RecommendedNumberOfInstancesToPurchase": rec_details.get("RecommendedNumberOfInstancesToPurchase", "0"),
                "UpfrontCost": f"${float(rec_details.get('UpfrontCost', '0')):.2f}",
                "RecurringStandardMonthlyCost": f"${float(rec_details.get('RecurringStandardMonthlyCost', '0')):.2f}",
                "EstimatedMonthlySavings": f"${float(rec_details.get('EstimatedMonthlySavingsAmount', '0')):.2f}",
                "EstimatedSavingsPercentage": f"{float(rec_details.get('EstimatedMonthlySavingsPercentage', '0')):.2f}%",
                "AverageUtilization": f"{float(rec_details.get('AverageUtilization', '0')):.2f}%",
                "MinimumNumberOfInstancesUsedPerHour": rec_details.get('MinimumNumberOfInstancesUsedPerHour', '0'),
                "MaximumNumberOfInstancesUsedPerHour": rec_details.get('MaximumNumberOfInstancesUsedPerHour', '0'),
            })
        
        total_monthly_savings = sum(
            float(item["EstimatedMonthlySavings"].replace("$", "").replace(",", ""))
            for item in output_data
        )
        
        fields = {
            "1": "Service",
            "2": "InstanceType",
            "3": "Platform",
            "4": "Region",
            "5": "RecommendedNumberOfInstancesToPurchase",
            "6": "UpfrontCost",
            "7": "RecurringStandardMonthlyCost",
            "8": "EstimatedMonthlySavings",
            "9": "EstimatedSavingsPercentage",
            "10": "AverageUtilization",
        }
        
        return {
            "id": 303,
            "name": f"Reserved Instance Recommendations - {service}",
            "fields": fields,
            "headers": fields_to_headers(fields),
            "count": len(output_data),
            "total_monthly_savings": f"${total_monthly_savings:.2f}",
            "resource": output_data,
        }
        
    except Exception as e:
        logger.error(f"Error getting Reserved Instance recommendations: {e}")
        raise


def analyze_reserved_instance_utilization(
    session: Any, region_name: str = "us-east-1"
) -> dict[str, Any]:
    """Analyze Reserved Instance utilization and coverage.
    
    Args:
        session: Boto3 session
        region_name: AWS region (Cost Explorer always uses us-east-1)
    
    Returns:
        Dictionary with Reserved Instance utilization analysis
    """
    ce_client = session.client("ce", region_name="us-east-1")
    
    output_data = []
    
    logger.info("Analyzing Reserved Instance utilization")
    
    try:
        # Get utilization for last 30 days
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        
        response = ce_client.get_reservation_utilization(
            TimePeriod={"Start": start_date, "End": end_date},
            Granularity="MONTHLY",
            GroupBy=[
                {"Type": "DIMENSION", "Key": "SERVICE"},
                {"Type": "DIMENSION", "Key": "INSTANCE_TYPE"}
            ]
        )
        
        for result in response.get("UtilizationsByTime", []):
            time_period = result.get("TimePeriod", {})
            groups = result.get("Groups", [])
            
            for group in groups:
                keys = group.get("Keys", [])
                service = keys[0] if len(keys) > 0 else "N/A"
                instance_type = keys[1] if len(keys) > 1 else "N/A"
                
                utilization = group.get("Utilization", {})
                utilization_percentage = utilization.get("UtilizationPercentage", "0")
                purchased_hours = utilization.get("PurchasedHours", "0")
                used_hours = utilization.get("UsedHours", "0")
                unused_hours = utilization.get("UnusedHours", "0")
                
                # Flag underutilized RIs (< 70% utilization)
                is_underutilized = float(utilization_percentage) < 70.0
                
                output_data.append({
                    "Service": service,
                    "InstanceType": instance_type,
                    "StartDate": time_period.get("Start", "N/A"),
                    "EndDate": time_period.get("End", "N/A"),
                    "UtilizationPercentage": f"{float(utilization_percentage):.2f}%",
                    "PurchasedHours": f"{float(purchased_hours):.2f}",
                    "UsedHours": f"{float(used_hours):.2f}",
                    "UnusedHours": f"{float(unused_hours):.2f}",
                    "IsUnderutilized": "Yes" if is_underutilized else "No",
                    "TotalAmortizedFee": utilization.get("TotalAmortizedFee", "0"),
                    "NetRISavings": utilization.get("NetRISavings", "0"),
                })
        
        # Calculate wasted spend from underutilized RIs
        wasted_spend = sum(
            float(item["TotalAmortizedFee"]) * (1 - float(item["UtilizationPercentage"].replace("%", "")) / 100)
            for item in output_data
            if item["IsUnderutilized"] == "Yes"
        )
        
        fields = {
            "1": "Service",
            "2": "InstanceType",
            "3": "StartDate",
            "4": "EndDate",
            "5": "UtilizationPercentage",
            "6": "PurchasedHours",
            "7": "UsedHours",
            "8": "UnusedHours",
            "9": "IsUnderutilized",
            "10": "TotalAmortizedFee",
            "11": "NetRISavings",
        }
        
        return {
            "id": 304,
            "name": "Reserved Instance Utilization Analysis",
            "fields": fields,
            "headers": fields_to_headers(fields),
            "count": len(output_data),
            "wasted_monthly_spend": f"${wasted_spend:.2f}",
            "resource": output_data,
        }
        
    except Exception as e:
        logger.error(f"Error analyzing Reserved Instance utilization: {e}")
        raise
