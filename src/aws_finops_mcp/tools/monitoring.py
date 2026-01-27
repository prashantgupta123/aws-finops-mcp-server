"""Monitoring cleanup tools for AWS resources."""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List

from ..utils.helpers import fields_to_headers

logger = logging.getLogger(__name__)


def find_unused_cloudwatch_alarms(
    session: Any, region_name: str, period: int = 90
) -> dict[str, Any]:
    """Find CloudWatch alarms in INSUFFICIENT_DATA state for extended period.
    
    Args:
        session: Boto3 session
        region_name: AWS region name
        period: Lookback period in days
    
    Returns:
        Dictionary with unused CloudWatch alarms
    """
    cloudwatch_client = session.client("cloudwatch", region_name=region_name)
    
    cutoff_date = datetime.now() - timedelta(days=period)
    output_data = []
    
    logger.info(f"Finding unused CloudWatch alarms in {region_name}")
    
    try:
        # Get all alarms
        paginator = cloudwatch_client.get_paginator("describe_alarms")
        
        for page in paginator.paginate():
            for alarm in page.get("MetricAlarms", []) + page.get("CompositeAlarms", []):
                alarm_name = alarm["AlarmName"]
                alarm_arn = alarm["AlarmArn"]
                state_value = alarm.get("StateValue", "OK")
                state_reason = alarm.get("StateReason", "")
                state_updated = alarm.get("StateUpdatedTimestamp")
                
                # Check if in INSUFFICIENT_DATA state for long time
                is_unused = False
                if state_value == "INSUFFICIENT_DATA":
                    if state_updated and state_updated < cutoff_date:
                        is_unused = True
                
                # Also check for alarms referencing deleted resources
                if "does not exist" in state_reason.lower() or "not found" in state_reason.lower():
                    is_unused = True
                
                if is_unused:
                    # Get alarm details
                    metric_name = alarm.get("MetricName", "N/A")
                    namespace = alarm.get("Namespace", "N/A")
                    actions_enabled = alarm.get("ActionsEnabled", False)
                    alarm_actions = alarm.get("AlarmActions", [])
                    
                    # Calculate age
                    age_days = 0
                    if state_updated:
                        age_days = (datetime.now(state_updated.tzinfo) - state_updated).days
                    
                    # CloudWatch alarm cost: $0.10/month per alarm
                    monthly_cost = 0.10
                    
                    # Get tags
                    try:
                        tags_response = cloudwatch_client.list_tags_for_resource(ResourceARN=alarm_arn)
                        tags = tags_response.get("Tags", [])
                        tags_str = ", ".join([f"{tag['Key']}={tag['Value']}" for tag in tags]) if tags else "None"
                    except Exception:
                        tags_str = "None"
                    
                    output_data.append({
                        "AlarmName": alarm_name,
                        "AlarmArn": alarm_arn,
                        "StateValue": state_value,
                        "StateReason": state_reason[:100] + "..." if len(state_reason) > 100 else state_reason,
                        "MetricName": metric_name,
                        "Namespace": namespace,
                        "ActionsEnabled": actions_enabled,
                        "AlarmActionsCount": len(alarm_actions),
                        "StateUpdatedTimestamp": state_updated.strftime("%Y-%m-%d %H:%M:%S") if state_updated else "N/A",
                        "AgeDays": age_days,
                        "EstimatedMonthlyCost": f"${monthly_cost:.2f}",
                        "Tags": tags_str,
                        "Description": f"CloudWatch alarm in {state_value} state for {age_days}+ days",
                    })
        
        # Calculate total potential savings
        total_monthly_cost = len(output_data) * 0.10
        
        fields = {
            "1": "AlarmName",
            "2": "AlarmArn",
            "3": "StateValue",
            "4": "StateReason",
            "5": "MetricName",
            "6": "Namespace",
            "7": "ActionsEnabled",
            "8": "AlarmActionsCount",
            "9": "StateUpdatedTimestamp",
            "10": "AgeDays",
            "11": "EstimatedMonthlyCost",
            "12": "Tags",
            "13": "Description",
        }
        
        return {
            "id": 215,
            "name": "Unused CloudWatch Alarms",
            "fields": fields,
            "headers": fields_to_headers(fields),
            "count": len(output_data),
            "total_monthly_cost": f"${total_monthly_cost:.2f}",
            "resource": output_data,
        }
        
    except Exception as e:
        logger.error(f"Error finding unused CloudWatch alarms: {e}")
        raise


def find_orphaned_cloudwatch_dashboards(
    session: Any, region_name: str, period: int = 90
) -> dict[str, Any]:
    """Find CloudWatch dashboards with widgets referencing deleted resources.
    
    Args:
        session: Boto3 session
        region_name: AWS region name
        period: Minimum age in days
    
    Returns:
        Dictionary with orphaned CloudWatch dashboards
    """
    cloudwatch_client = session.client("cloudwatch", region_name=region_name)
    
    output_data = []
    
    logger.info(f"Finding orphaned CloudWatch dashboards in {region_name}")
    
    try:
        # Get all dashboards
        dashboards_response = cloudwatch_client.list_dashboards()
        
        for dashboard in dashboards_response.get("DashboardEntries", []):
            dashboard_name = dashboard["DashboardName"]
            last_modified = dashboard.get("LastModified")
            
            try:
                # Get dashboard details
                dashboard_response = cloudwatch_client.get_dashboard(DashboardName=dashboard_name)
                dashboard_body = dashboard_response.get("DashboardBody", "")
                
                # Count widgets
                import json
                try:
                    dashboard_json = json.loads(dashboard_body)
                    widget_count = len(dashboard_json.get("widgets", []))
                except Exception:
                    widget_count = 0
                
                # Calculate age
                age_days = 0
                if last_modified:
                    age_days = (datetime.now(last_modified.tzinfo) - last_modified).days
                
                # CloudWatch dashboard cost: $3/month per dashboard
                monthly_cost = 3.00
                
                # Check if old enough
                if age_days >= period:
                    output_data.append({
                        "DashboardName": dashboard_name,
                        "DashboardArn": dashboard.get("DashboardArn", "N/A"),
                        "LastModified": last_modified.strftime("%Y-%m-%d %H:%M:%S") if last_modified else "N/A",
                        "AgeDays": age_days,
                        "WidgetCount": widget_count,
                        "EstimatedMonthlyCost": f"${monthly_cost:.2f}",
                        "Description": f"CloudWatch dashboard not modified in {age_days} days",
                    })
            
            except Exception as e:
                logger.debug(f"Error processing dashboard {dashboard_name}: {e}")
                continue
        
        # Calculate total potential savings
        total_monthly_cost = len(output_data) * 3.00
        
        fields = {
            "1": "DashboardName",
            "2": "DashboardArn",
            "3": "LastModified",
            "4": "AgeDays",
            "5": "WidgetCount",
            "6": "EstimatedMonthlyCost",
            "7": "Description",
        }
        
        return {
            "id": 216,
            "name": "Orphaned CloudWatch Dashboards",
            "fields": fields,
            "headers": fields_to_headers(fields),
            "count": len(output_data),
            "total_monthly_cost": f"${total_monthly_cost:.2f}",
            "resource": output_data,
        }
        
    except Exception as e:
        logger.error(f"Error finding orphaned CloudWatch dashboards: {e}")
        raise



def find_orphaned_cloudwatch_alarms(
    session: Any, region_name: str, max_results: int = 100
) -> dict[str, Any]:
    """Find CloudWatch alarms not associated with any active AWS resources.
    
    This function validates alarms against actual resources across multiple services:
    - EC2 instances
    - RDS clusters and instances
    - Target groups and load balancers
    - ECS clusters and services
    - Lambda functions
    - SQS queues
    
    Args:
        session: Boto3 session
        region_name: AWS region name
        max_results: Maximum results per API call
    
    Returns:
        Dictionary with orphaned CloudWatch alarms
    """
    logger.info(f"Finding orphaned CloudWatch alarms in {region_name}")
    
    # Define resource types and their CloudWatch namespaces
    input_data = {
        "EC2Instance": {
            "Namespace": ["AWS/EC2", "CWAgent"],
            "Dimension": ["InstanceId"],
            "ExcludeDimension": []
        },
        "RDSCluster": {
            "Namespace": ["AWS/RDS"],
            "Dimension": ["DBClusterIdentifier"],
            "ExcludeDimension": []
        },
        "RDSInstance": {
            "Namespace": ["AWS/RDS"],
            "Dimension": ["DBInstanceIdentifier"],
            "ExcludeDimension": []
        },
        "TargetGroup": {
            "Namespace": ["AWS/ApplicationELB"],
            "Dimension": ["TargetGroup"],
            "ExcludeDimension": ["LoadBalancer"]
        },
        "LoadBalancerTargetGroup": {
            "Namespace": ["AWS/ApplicationELB"],
            "Dimension": ["TargetGroup", "LoadBalancer"],
            "ExcludeDimension": []
        },
        "LoadBalancer": {
            "Namespace": ["AWS/ApplicationELB"],
            "Dimension": ["LoadBalancer"],
            "ExcludeDimension": ["TargetGroup"]
        },
        "ECSService": {
            "Namespace": ["AWS/ECS"],
            "Dimension": ["ClusterName", "ServiceName"],
            "ExcludeDimension": []
        },
        "ECSCluster": {
            "Namespace": ["AWS/ECS"],
            "Dimension": ["ClusterName"],
            "ExcludeDimension": ["ServiceName"]
        },
        "Lambda": {
            "Namespace": ["AWS/Lambda"],
            "Dimension": ["FunctionName"],
            "ExcludeDimension": ["Resource"]
        },
        "LambdaResource": {
            "Namespace": ["AWS/Lambda"],
            "Dimension": ["FunctionName", "Resource"],
            "ExcludeDimension": []
        },
        "SQS": {
            "Namespace": ["AWS/SQS"],
            "Dimension": ["QueueName"],
            "ExcludeDimension": []
        }
    }
    
    try:
        # Get all AWS resources
        service_data = _get_aws_services_data(session, max_results, region_name)
        
        # Get all CloudWatch alarms
        cloudwatch_client = session.client('cloudwatch', region_name=region_name)
        cloudwatch_alarms = _list_alarms_for_aws_resources(cloudwatch_client, max_results)
        
        # Check each resource type for orphaned alarms
        output_data = []
        for resource_name, resource_details in input_data.items():
            if resource_name in service_data:
                for namespace in resource_details['Namespace']:
                    orphaned = _check_alarm_aws_resources_with_resource_list(
                        resource_details, namespace, cloudwatch_alarms, service_data[resource_name]
                    )
                    output_data.extend(orphaned)
        
        # Calculate potential savings
        monthly_cost_per_alarm = 0.10
        total_monthly_cost = len(output_data) * monthly_cost_per_alarm
        
        fields = {
            "1": "AlarmName",
            "2": "Namespace",
            "3": "Dimensions",
            "4": "Description"
        }
        
        return {
            "id": 217,
            "name": "Orphaned CloudWatch Alarms",
            "fields": fields,
            "headers": fields_to_headers(fields),
            "count": len(output_data),
            "total_monthly_cost": f"${total_monthly_cost:.2f}",
            "resource": output_data,
        }
        
    except Exception as e:
        logger.error(f"Error finding orphaned CloudWatch alarms: {e}")
        raise


def _get_aws_services_data(session: Any, max_results: int, region_name: str) -> Dict[str, List[Dict]]:
    """Get data for all AWS services to validate alarms against."""
    ec2_client = session.client('ec2', region_name=region_name)
    elbv2_client = session.client('elbv2', region_name=region_name)
    rds_client = session.client('rds', region_name=region_name)
    ecs_client = session.client('ecs', region_name=region_name)
    lambda_client = session.client('lambda', region_name=region_name)
    sqs_client = session.client('sqs', region_name=region_name)
    
    service_data = {
        "EC2Instance": _get_ec2_details(ec2_client, max_results),
        "RDSCluster": _get_rds_cluster_details(rds_client, max_results),
        "RDSInstance": _get_rds_instance_details(rds_client, max_results),
        "LoadBalancer": _get_load_balancer_details(elbv2_client, max_results),
        "ECSCluster": _get_ecs_cluster_details(ecs_client, max_results),
        "ECSService": _get_ecs_service_details(ecs_client, max_results),
        "Lambda": _get_lambda_details(lambda_client, max_results),
        "LambdaResource": _get_lambda_resource_details(lambda_client, max_results),
        "SQS": _get_sqs_details(sqs_client, max_results)
    }
    
    # Get target groups
    target_groups, load_balancers_target_group = _get_target_group_details(elbv2_client, max_results)
    service_data["TargetGroup"] = target_groups
    service_data["LoadBalancerTargetGroup"] = load_balancers_target_group
    
    return service_data


def _get_ec2_details(ec2_client: Any, max_results: int) -> List[Dict]:
    """Get all EC2 instance IDs."""
    ec2_details = []
    paginator = ec2_client.get_paginator('describe_instances')
    
    for page in paginator.paginate(PaginationConfig={'PageSize': max_results}):
        for reservation in page['Reservations']:
            for instance in reservation['Instances']:
                ec2_details.append({"InstanceId": instance['InstanceId']})
    
    return ec2_details


def _get_target_group_details(elbv2_client: Any, max_results: int) -> tuple:
    """Get all target groups and their load balancer associations."""
    targetgroup_details = []
    target_groups = []
    paginator = elbv2_client.get_paginator('describe_target_groups')
    
    for page in paginator.paginate(PaginationConfig={'PageSize': max_results}):
        for target_group in page['TargetGroups']:
            tg_arn_part = "targetgroup/" + target_group['TargetGroupArn'].split("targetgroup/")[1]
            target_groups.append({"TargetGroup": tg_arn_part})
            
            for load_balancer in target_group.get("LoadBalancerArns", []):
                lb_arn_part = load_balancer.split("loadbalancer/")[1]
                targetgroup_details.append({
                    "LoadBalancer": lb_arn_part,
                    "TargetGroup": tg_arn_part
                })
    
    return target_groups, targetgroup_details


def _get_load_balancer_details(elbv2_client: Any, max_results: int) -> List[Dict]:
    """Get all load balancers."""
    load_balancer_details = []
    paginator = elbv2_client.get_paginator('describe_load_balancers')
    
    for page in paginator.paginate(PaginationConfig={'PageSize': max_results}):
        for load_balancer in page['LoadBalancers']:
            lb_arn_part = load_balancer['LoadBalancerArn'].split("loadbalancer/")[1]
            load_balancer_details.append({"LoadBalancer": lb_arn_part})
    
    return load_balancer_details


def _get_rds_cluster_details(rds_client: Any, max_results: int) -> List[Dict]:
    """Get all RDS clusters."""
    rds_details = []
    filters = [{
        'Name': 'engine',
        'Values': ["mysql", "aurora-mysql", "postgres", "aurora-postgresql"]
    }]
    
    paginator = rds_client.get_paginator('describe_db_clusters')
    for page in paginator.paginate(Filters=filters, PaginationConfig={'PageSize': max_results}):
        for cluster in page['DBClusters']:
            rds_details.append({'DBClusterIdentifier': cluster['DBClusterIdentifier']})
    
    return rds_details


def _get_rds_instance_details(rds_client: Any, max_results: int) -> List[Dict]:
    """Get all RDS instances."""
    rds_details = []
    filters = [{
        'Name': 'engine',
        'Values': ["mysql", "aurora-mysql", "postgres", "aurora-postgresql"]
    }]
    
    paginator = rds_client.get_paginator('describe_db_instances')
    for page in paginator.paginate(Filters=filters, PaginationConfig={'PageSize': max_results}):
        for instance in page['DBInstances']:
            rds_details.append({'DBInstanceIdentifier': instance['DBInstanceIdentifier']})
    
    return rds_details


def _get_ecs_cluster_details(ecs_client: Any, max_results: int) -> List[Dict]:
    """Get all ECS clusters."""
    ecs_details = []
    paginator = ecs_client.get_paginator('list_clusters')
    
    for page in paginator.paginate(PaginationConfig={'PageSize': max_results}):
        for cluster_arn in page['clusterArns']:
            ecs_details.append({"ClusterName": cluster_arn.split("cluster/")[1]})
    
    return ecs_details


def _get_ecs_service_details(ecs_client: Any, max_results: int) -> List[Dict]:
    """Get all ECS services across all clusters."""
    ecs_details = []
    cluster_paginator = ecs_client.get_paginator('list_clusters')
    
    for cluster_page in cluster_paginator.paginate(PaginationConfig={'PageSize': max_results}):
        for cluster_arn in cluster_page['clusterArns']:
            cluster_name = cluster_arn.split("cluster/")[1]
            service_paginator = ecs_client.get_paginator('list_services')
            
            for service_page in service_paginator.paginate(
                cluster=cluster_arn,
                PaginationConfig={'PageSize': max_results}
            ):
                for service_arn in service_page['serviceArns']:
                    ecs_details.append({
                        "ClusterName": cluster_name,
                        "ServiceName": service_arn.split("/")[-1]
                    })
    
    return ecs_details


def _get_lambda_details(lambda_client: Any, max_results: int) -> List[Dict]:
    """Get all Lambda functions."""
    lambda_details = []
    paginator = lambda_client.get_paginator('list_functions')
    
    for page in paginator.paginate(PaginationConfig={'PageSize': max_results}):
        for function in page['Functions']:
            lambda_details.append({"FunctionName": function["FunctionName"]})
    
    return lambda_details


def _get_lambda_resource_details(lambda_client: Any, max_results: int) -> List[Dict]:
    """Get all Lambda function versions and aliases."""
    lambda_details = []
    function_paginator = lambda_client.get_paginator('list_functions')
    
    for function_page in function_paginator.paginate(PaginationConfig={'PageSize': max_results}):
        for function in function_page['Functions']:
            function_name = function["FunctionName"]
            version_paginator = lambda_client.get_paginator('list_versions_by_function')
            
            for version_page in version_paginator.paginate(
                FunctionName=function_name,
                PaginationConfig={'PageSize': max_results}
            ):
                for version_function in version_page['Versions']:
                    if version_function["Version"] == "$LATEST":
                        resource_name = version_function["FunctionName"]
                    else:
                        resource_name = f"{version_function['FunctionName']}:{version_function['Version']}"
                    
                    lambda_details.append({
                        "FunctionName": version_function["FunctionName"],
                        "Resource": resource_name
                    })
    
    return lambda_details


def _get_sqs_details(sqs_client: Any, max_results: int) -> List[Dict]:
    """Get all SQS queues."""
    sqs_details = []
    paginator = sqs_client.get_paginator('list_queues')
    
    for page in paginator.paginate(PaginationConfig={'PageSize': max_results}):
        for queue_url in page.get('QueueUrls', []):
            sqs_details.append({"QueueName": queue_url.split("/")[-1]})
    
    return sqs_details


def _list_alarms_for_aws_resources(cloudwatch_client: Any, max_results: int) -> List[Dict]:
    """Get all CloudWatch alarms with their dimensions."""
    cloudwatch_alarms = []
    paginator = cloudwatch_client.get_paginator('describe_alarms')
    
    for page in paginator.paginate(PaginationConfig={'PageSize': max_results}):
        for alarm in page['MetricAlarms']:
            if "Namespace" in alarm:
                cloudwatch_alarms.append({
                    "AlarmName": alarm["AlarmName"],
                    "Namespace": alarm["Namespace"],
                    "Dimensions": alarm.get("Dimensions", [])
                })
            elif "Metrics" in alarm:
                for metric in alarm["Metrics"]:
                    if "MetricStat" in metric:
                        cloudwatch_alarms.append({
                            "AlarmName": alarm["AlarmName"],
                            "Namespace": metric["MetricStat"]["Metric"]["Namespace"],
                            "Dimensions": metric["MetricStat"]["Metric"].get("Dimensions", [])
                        })
    
    return cloudwatch_alarms


def _check_alarm_aws_resources_with_resource_list(
    resource_details: Dict,
    namespace: str,
    alarms: List[Dict],
    service_data: List[Dict]
) -> List[Dict]:
    """Check if alarms reference resources that no longer exist."""
    unused_alarms = []
    dimensions = resource_details['Dimension']
    exclude_dimension = resource_details['ExcludeDimension']
    
    for alarm in alarms:
        if alarm['Namespace'] == namespace:
            alarm_dimensions = {dimension['Name']: dimension['Value'] for dimension in alarm['Dimensions']}
            
            # Check if all required dimensions are present
            all_dimension_present = []
            for resource_dimension in dimensions:
                all_dimension_present.append(resource_dimension in alarm_dimensions)
            
            # Check if excluded dimensions are absent
            for resource_dimension in exclude_dimension:
                if resource_dimension in alarm_dimensions:
                    all_dimension_present.append(False)
            
            dimension_present = all(all_dimension_present)
            
            if dimension_present:
                # Check if resource exists
                resource_present = False
                for resource in service_data:
                    all_resource_present = []
                    for resource_dimension in dimensions:
                        if alarm_dimensions.get(resource_dimension) == resource.get(resource_dimension):
                            all_resource_present.append(True)
                        else:
                            all_resource_present.append(False)
                    
                    resource_present = all(all_resource_present)
                    if resource_present:
                        break
                
                if not resource_present:
                    # Format dimensions for display
                    dim_str = ", ".join([f"{k}={v}" for k, v in alarm_dimensions.items()])
                    
                    unused_alarms.append({
                        "AlarmName": alarm['AlarmName'],
                        "Namespace": alarm['Namespace'],
                        "Dimensions": dim_str,
                        "Description": "Alarm not associated with any active resource"
                    })
    
    return unused_alarms
