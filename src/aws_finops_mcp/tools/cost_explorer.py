"""Cost Explorer tools for AWS cost analysis."""

import logging
from datetime import datetime, timedelta
from typing import Any

from ..utils.helpers import fields_to_headers

logger = logging.getLogger(__name__)


def get_cost_by_region(
    session: Any,
    region_name: str,
    start_date: str | None = None,
    end_date: str | None = None,
) -> dict[str, Any]:
    """Get cost breakdown by region for the specified period.
    
    Args:
        session: Boto3 session
        region_name: AWS region (Cost Explorer is global, but session needs region)
        start_date: Start date in YYYY-MM-DD format (default: first day of last month)
        end_date: End date in YYYY-MM-DD format (default: first day of current month)
    
    Returns:
        Dictionary with cost breakdown by region
    """
    # Calculate date range if not provided
    if not start_date or not end_date:
        today = datetime.now()
        first_day_current_month = today.replace(day=1)
        last_day_previous_month = first_day_current_month - timedelta(days=1)
        first_day_previous_month = last_day_previous_month.replace(day=1)
        
        start_date = first_day_previous_month.strftime("%Y-%m-%d")
        end_date = first_day_current_month.strftime("%Y-%m-%d")
    
    logger.info(f"Getting cost breakdown for period {start_date} to {end_date}")
    
    # Create Cost Explorer client (always use us-east-1)
    ce_client = session.client("ce", region_name="us-east-1")
    
    try:
        # Query Cost Explorer API for regions
        region_response = ce_client.get_cost_and_usage(
            TimePeriod={"Start": start_date, "End": end_date},
            Granularity="MONTHLY",
            Metrics=["UnblendedCost"],
            GroupBy=[{"Type": "DIMENSION", "Key": "REGION"}],
        )
        
        # Process response to extract region-wise costs
        regions = []
        for time_period in region_response["ResultsByTime"]:
            for group in time_period["Groups"]:
                region = group["Keys"][0] if group["Keys"][0] else "No Region"
                cost = round(float(group["Metrics"]["UnblendedCost"]["Amount"]), 2)
                
                if cost > 0:
                    regions.append({
                        "Region": region,
                        "Cost": cost,
                        "Currency": "USD",
                        "Period": f"{start_date} to {end_date}",
                        "Description": f"Total cost for {region} region",
                    })
        
        # Sort by cost descending
        regions.sort(key=lambda x: x["Cost"], reverse=True)
        
        # Calculate total
        total_cost = sum(r["Cost"] for r in regions)
        
        fields = {
            "1": "Region",
            "2": "Cost",
            "3": "Currency",
            "4": "Period",
            "5": "Description",
        }
        
        return {
            "id": 301,
            "name": "Cost by Region",
            "fields": fields,
            "headers": fields_to_headers(fields),
            "count": len(regions),
            "total_cost": total_cost,
            "resource": regions,
        }
        
    except Exception as e:
        logger.error(f"Error getting cost by region: {e}")
        raise


def get_cost_by_service(
    session: Any,
    region_name: str,
    start_date: str | None = None,
    end_date: str | None = None,
) -> dict[str, Any]:
    """Get cost breakdown by service for the specified period.
    
    Args:
        session: Boto3 session
        region_name: AWS region (Cost Explorer is global, but session needs region)
        start_date: Start date in YYYY-MM-DD format (default: first day of last month)
        end_date: End date in YYYY-MM-DD format (default: first day of current month)
    
    Returns:
        Dictionary with cost breakdown by service
    """
    # Calculate date range if not provided
    if not start_date or not end_date:
        today = datetime.now()
        first_day_current_month = today.replace(day=1)
        last_day_previous_month = first_day_current_month - timedelta(days=1)
        first_day_previous_month = last_day_previous_month.replace(day=1)
        
        start_date = first_day_previous_month.strftime("%Y-%m-%d")
        end_date = first_day_current_month.strftime("%Y-%m-%d")
    
    logger.info(f"Getting cost breakdown by service for period {start_date} to {end_date}")
    
    # Create Cost Explorer client (always use us-east-1)
    ce_client = session.client("ce", region_name="us-east-1")
    
    try:
        # Query Cost Explorer API for services
        service_response = ce_client.get_cost_and_usage(
            TimePeriod={"Start": start_date, "End": end_date},
            Granularity="MONTHLY",
            Metrics=["UnblendedCost"],
            GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}],
        )
        
        # Process response to extract service-wise costs
        services = []
        for time_period in service_response["ResultsByTime"]:
            for group in time_period["Groups"]:
                service = group["Keys"][0] if group["Keys"][0] else "No Service"
                cost = round(float(group["Metrics"]["UnblendedCost"]["Amount"]), 2)
                
                if cost > 0:
                    services.append({
                        "Service": service,
                        "Cost": cost,
                        "Currency": "USD",
                        "Period": f"{start_date} to {end_date}",
                        "Description": f"Total cost for {service}",
                    })
        
        # Sort by cost descending
        services.sort(key=lambda x: x["Cost"], reverse=True)
        
        # Calculate total
        total_cost = sum(s["Cost"] for s in services)
        
        fields = {
            "1": "Service",
            "2": "Cost",
            "3": "Currency",
            "4": "Period",
            "5": "Description",
        }
        
        return {
            "id": 302,
            "name": "Cost by Service",
            "fields": fields,
            "headers": fields_to_headers(fields),
            "count": len(services),
            "total_cost": total_cost,
            "resource": services,
        }
        
    except Exception as e:
        logger.error(f"Error getting cost by service: {e}")
        raise


def get_cost_by_region_and_service(
    session: Any,
    region_name: str,
    start_date: str | None = None,
    end_date: str | None = None,
) -> dict[str, Any]:
    """Get cost breakdown by region and service for the specified period.
    
    Args:
        session: Boto3 session
        region_name: AWS region (Cost Explorer is global, but session needs region)
        start_date: Start date in YYYY-MM-DD format (default: first day of last month)
        end_date: End date in YYYY-MM-DD format (default: first day of current month)
    
    Returns:
        Dictionary with cost breakdown by region and service
    """
    # Calculate date range if not provided
    if not start_date or not end_date:
        today = datetime.now()
        first_day_current_month = today.replace(day=1)
        last_day_previous_month = first_day_current_month - timedelta(days=1)
        first_day_previous_month = last_day_previous_month.replace(day=1)
        
        start_date = first_day_previous_month.strftime("%Y-%m-%d")
        end_date = first_day_current_month.strftime("%Y-%m-%d")
    
    logger.info(f"Getting cost breakdown by region and service for period {start_date} to {end_date}")
    
    # Create Cost Explorer client (always use us-east-1)
    ce_client = session.client("ce", region_name="us-east-1")
    
    try:
        # Query Cost Explorer API for region and service combination
        response = ce_client.get_cost_and_usage(
            TimePeriod={"Start": start_date, "End": end_date},
            Granularity="MONTHLY",
            Metrics=["UnblendedCost"],
            GroupBy=[
                {"Type": "DIMENSION", "Key": "REGION"},
                {"Type": "DIMENSION", "Key": "SERVICE"},
            ],
        )
        
        # Process response to extract region-service costs
        region_services = []
        for time_period in response["ResultsByTime"]:
            for group in time_period["Groups"]:
                region = group["Keys"][0] if group["Keys"][0] else "No Region"
                service = (
                    group["Keys"][1]
                    if len(group["Keys"]) > 1 and group["Keys"][1]
                    else "No Service"
                )
                cost = round(float(group["Metrics"]["UnblendedCost"]["Amount"]), 2)
                
                if cost > 0:
                    region_services.append({
                        "Region": region,
                        "Service": service,
                        "Cost": cost,
                        "Currency": "USD",
                        "Period": f"{start_date} to {end_date}",
                        "Description": f"{service} cost in {region}",
                    })
        
        # Sort by cost descending
        region_services.sort(key=lambda x: x["Cost"], reverse=True)
        
        # Calculate total
        total_cost = sum(rs["Cost"] for rs in region_services)
        
        fields = {
            "1": "Region",
            "2": "Service",
            "3": "Cost",
            "4": "Currency",
            "5": "Period",
            "6": "Description",
        }
        
        return {
            "id": 303,
            "name": "Cost by Region and Service",
            "fields": fields,
            "headers": fields_to_headers(fields),
            "count": len(region_services),
            "total_cost": total_cost,
            "resource": region_services,
        }
        
    except Exception as e:
        logger.error(f"Error getting cost by region and service: {e}")
        raise


def get_daily_cost_trend(
    session: Any,
    region_name: str,
    days: int = 30,
) -> dict[str, Any]:
    """Get daily cost trend for the specified number of days.
    
    Args:
        session: Boto3 session
        region_name: AWS region (Cost Explorer is global, but session needs region)
        days: Number of days to look back (default: 30)
    
    Returns:
        Dictionary with daily cost trend
    """
    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")
    
    logger.info(f"Getting daily cost trend for {days} days ({start_date_str} to {end_date_str})")
    
    # Create Cost Explorer client (always use us-east-1)
    ce_client = session.client("ce", region_name="us-east-1")
    
    try:
        # Query Cost Explorer API for daily costs
        response = ce_client.get_cost_and_usage(
            TimePeriod={"Start": start_date_str, "End": end_date_str},
            Granularity="DAILY",
            Metrics=["UnblendedCost"],
        )
        
        # Process response to extract daily costs
        daily_costs = []
        for time_period in response["ResultsByTime"]:
            date = time_period["TimePeriod"]["Start"]
            cost = round(float(time_period["Total"]["UnblendedCost"]["Amount"]), 2)
            
            daily_costs.append({
                "Date": date,
                "Cost": cost,
                "Currency": "USD",
                "Description": f"Total cost for {date}",
            })
        
        # Calculate statistics
        costs = [dc["Cost"] for dc in daily_costs]
        total_cost = sum(costs)
        avg_cost = total_cost / len(costs) if costs else 0
        max_cost = max(costs) if costs else 0
        min_cost = min(costs) if costs else 0
        
        fields = {
            "1": "Date",
            "2": "Cost",
            "3": "Currency",
            "4": "Description",
        }
        
        return {
            "id": 304,
            "name": "Daily Cost Trend",
            "fields": fields,
            "headers": fields_to_headers(fields),
            "count": len(daily_costs),
            "total_cost": round(total_cost, 2),
            "average_cost": round(avg_cost, 2),
            "max_cost": round(max_cost, 2),
            "min_cost": round(min_cost, 2),
            "period_days": days,
            "resource": daily_costs,
        }
        
    except Exception as e:
        logger.error(f"Error getting daily cost trend: {e}")
        raise
