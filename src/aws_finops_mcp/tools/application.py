"""Application performance monitoring tools."""

import logging
from datetime import datetime, timedelta
from typing import Any

from ..utils.helpers import fields_to_headers

logger = logging.getLogger(__name__)


def find_target_groups_with_high_error_rate(
    session: Any, region_name: str, period: int, error_threshold: float = 5.0
) -> dict[str, Any]:
    """Find target groups with high error rates."""
    elb_client = session.client("elbv2", region_name=region_name)
    cloudwatch_client = session.client("cloudwatch", region_name=region_name)
    
    start_time = datetime.now() - timedelta(days=period)
    end_time = datetime.now()
    
    high_error_tgs = []
    response = elb_client.describe_target_groups()
    
    for tg in response["TargetGroups"]:
        tg_arn = tg["TargetGroupArn"]
        tg_name = tg["TargetGroupName"]
        
        # Get target group full name for CloudWatch dimensions
        tg_full_name = tg_arn.split(":targetgroup/")[1]
        
        # Get associated load balancers
        lb_arns = tg.get("LoadBalancerArns", [])
        if not lb_arns:
            continue
        
        for lb_arn in lb_arns:
            lb_full_name = lb_arn.split(":loadbalancer/")[1]
            
            # Get HTTP 5XX count
            http_5xx_response = cloudwatch_client.get_metric_statistics(
                Namespace="AWS/ApplicationELB",
                MetricName="HTTPCode_Target_5XX_Count",
                Dimensions=[
                    {"Name": "LoadBalancer", "Value": lb_full_name},
                    {"Name": "TargetGroup", "Value": tg_full_name},
                ],
                StartTime=start_time,
                EndTime=end_time,
                Period=86400,
                Statistics=["Sum"],
            )
            
            # Get request count
            request_response = cloudwatch_client.get_metric_statistics(
                Namespace="AWS/ApplicationELB",
                MetricName="RequestCount",
                Dimensions=[
                    {"Name": "LoadBalancer", "Value": lb_full_name},
                    {"Name": "TargetGroup", "Value": tg_full_name},
                ],
                StartTime=start_time,
                EndTime=end_time,
                Period=86400,
                Statistics=["Sum"],
            )
            
            # Calculate error rate
            total_5xx = sum(dp["Sum"] for dp in http_5xx_response.get("Datapoints", []))
            total_requests = sum(dp["Sum"] for dp in request_response.get("Datapoints", []))
            
            if total_requests > 0:
                error_rate = (total_5xx / total_requests) * 100
                
                if error_rate >= error_threshold:
                    high_error_tgs.append({
                        "TargetGroupName": tg_name,
                        "LoadBalancer": lb_full_name.split("/")[1],
                        "Protocol": tg.get("Protocol", ""),
                        "Port": tg.get("Port", 0),
                        "TotalRequests": int(total_requests),
                        "Total5XXErrors": int(total_5xx),
                        "ErrorRate": f"{error_rate:.2f}%",
                        "Description": f"Target group has {error_rate:.2f}% error rate (threshold: {error_threshold}%)",
                    })
    
    fields = {
        "1": "TargetGroupName",
        "2": "LoadBalancer",
        "3": "Protocol",
        "4": "Port",
        "5": "TotalRequests",
        "6": "Total5XXErrors",
        "7": "ErrorRate",
        "8": "Description",
    }
    
    return {
        "id": 115,
        "name": "Target Group Error Rate",
        "fields": fields,
        "headers": fields_to_headers(fields),
        "count": len(high_error_tgs),
        "resource": high_error_tgs,
    }


def find_target_groups_with_high_response_time(
    session: Any, region_name: str, period: int, response_time_threshold: float = 1.0
) -> dict[str, Any]:
    """Find target groups with high response times."""
    elb_client = session.client("elbv2", region_name=region_name)
    cloudwatch_client = session.client("cloudwatch", region_name=region_name)
    
    start_time = datetime.now() - timedelta(days=period)
    end_time = datetime.now()
    
    high_response_tgs = []
    response = elb_client.describe_target_groups()
    
    for tg in response["TargetGroups"]:
        tg_arn = tg["TargetGroupArn"]
        tg_name = tg["TargetGroupName"]
        
        # Get target group full name for CloudWatch dimensions
        tg_full_name = tg_arn.split(":targetgroup/")[1]
        
        # Get associated load balancers
        lb_arns = tg.get("LoadBalancerArns", [])
        if not lb_arns:
            continue
        
        for lb_arn in lb_arns:
            lb_full_name = lb_arn.split(":loadbalancer/")[1]
            
            # Get target response time
            response_time_response = cloudwatch_client.get_metric_statistics(
                Namespace="AWS/ApplicationELB",
                MetricName="TargetResponseTime",
                Dimensions=[
                    {"Name": "LoadBalancer", "Value": lb_full_name},
                    {"Name": "TargetGroup", "Value": tg_full_name},
                ],
                StartTime=start_time,
                EndTime=end_time,
                Period=86400,
                Statistics=["Average", "Maximum"],
            )
            
            datapoints = response_time_response.get("Datapoints", [])
            if not datapoints:
                continue
            
            avg_response_time = sum(dp["Average"] for dp in datapoints) / len(datapoints)
            max_response_time = max(dp["Maximum"] for dp in datapoints)
            
            if avg_response_time >= response_time_threshold:
                high_response_tgs.append({
                    "TargetGroupName": tg_name,
                    "LoadBalancer": lb_full_name.split("/")[1],
                    "Protocol": tg.get("Protocol", ""),
                    "Port": tg.get("Port", 0),
                    "AvgResponseTime": f"{avg_response_time:.3f}s",
                    "MaxResponseTime": f"{max_response_time:.3f}s",
                    "Threshold": f"{response_time_threshold}s",
                    "Description": f"Target group has {avg_response_time:.3f}s avg response time (threshold: {response_time_threshold}s)",
                })
    
    fields = {
        "1": "TargetGroupName",
        "2": "LoadBalancer",
        "3": "Protocol",
        "4": "Port",
        "5": "AvgResponseTime",
        "6": "MaxResponseTime",
        "7": "Threshold",
        "8": "Description",
    }
    
    return {
        "id": 116,
        "name": "Target Group Response Time",
        "fields": fields,
        "headers": fields_to_headers(fields),
        "count": len(high_response_tgs),
        "resource": high_response_tgs,
    }
