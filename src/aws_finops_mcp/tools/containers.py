"""Container cleanup tools for AWS resources."""

import logging
from datetime import datetime, timedelta
from typing import Any

from ..utils.helpers import fields_to_headers

logger = logging.getLogger(__name__)


def find_old_ecs_task_definitions(
    session: Any, region_name: str, period: int = 90, max_results: int = 100
) -> dict[str, Any]:
    """Find ECS task definition revisions not used by any running service.
    
    This function identifies task definition revisions that are registered (ACTIVE or INACTIVE)
    but are not currently being used by any ECS service. This helps clean up unused revisions
    that accumulate over time.
    
    Args:
        session: Boto3 session
        region_name: AWS region name
        period: Not used (kept for API compatibility)
        max_results: Maximum results per API call
    
    Returns:
        Dictionary with unused ECS task definition revisions
    """
    ecs_client = session.client("ecs", region_name=region_name)
    
    output_data = []
    
    logger.info(f"Finding unused ECS task definition revisions in {region_name}")
    
    try:
        # Step 1: Get all task definitions used by services
        used_task_definitions = _get_used_task_definitions(ecs_client, max_results)
        
        # Step 2: Get all task definition revisions (ACTIVE and INACTIVE)
        all_revisions = _get_all_task_definition_revisions(ecs_client, max_results)
        
        # Step 3: Find unused revisions
        for family_name, all_family_revisions in all_revisions.items():
            # Get revisions used by services for this family
            used_revisions = set()
            for cluster_name, services in used_task_definitions.items():
                for service_name, families in services.items():
                    if family_name in families:
                        used_revisions.add(families[family_name])
            
            # Find unused revisions
            unused_revisions = [rev for rev in all_family_revisions if rev not in used_revisions]
            
            if unused_revisions:
                output_data.append({
                    "TaskDefinitionFamily": family_name,
                    "UnusedRevisions": ", ".join(str(r) for r in sorted(unused_revisions)),
                    "UnusedCount": len(unused_revisions),
                    "TotalRevisions": len(all_family_revisions),
                    "UsedRevisions": ", ".join(str(r) for r in sorted(used_revisions)) if used_revisions else "None",
                    "Description": f"Task definition has {len(unused_revisions)} unused revision(s) not associated with any running services",
                })
        
        fields = {
            "1": "TaskDefinitionFamily",
            "2": "UnusedRevisions",
            "3": "UnusedCount",
            "4": "TotalRevisions",
            "5": "UsedRevisions",
            "6": "Description",
        }
        
        return {
            "id": 207,
            "name": "Unused ECS Task Definition Revisions",
            "fields": fields,
            "headers": fields_to_headers(fields),
            "count": len(output_data),
            "resource": output_data,
        }
        
    except Exception as e:
        logger.error(f"Error finding unused ECS task definitions: {e}")
        raise


def _get_used_task_definitions(ecs_client: Any, max_results: int) -> dict:
    """Get task definitions currently used by ECS services."""
    cluster_details = {}
    
    # Get all clusters
    clusters_paginator = ecs_client.get_paginator("list_clusters")
    for clusters_page in clusters_paginator.paginate(PaginationConfig={"PageSize": max_results}):
        for cluster_arn in clusters_page.get("clusterArns", []):
            cluster_name = cluster_arn.split("/")[-1]
            service_list = {}
            
            # Get all services for this cluster
            services_paginator = ecs_client.get_paginator("list_services")
            for services_page in services_paginator.paginate(
                cluster=cluster_arn,
                PaginationConfig={"PageSize": max_results}
            ):
                service_arns = services_page.get("serviceArns", [])
                
                if service_arns:
                    # Batch describe services (up to 10 at a time)
                    for i in range(0, len(service_arns), 10):
                        batch_arns = service_arns[i:i+10]
                        try:
                            services_response = ecs_client.describe_services(
                                cluster=cluster_arn,
                                services=batch_arns
                            )
                            
                            for service in services_response.get("services", []):
                                service_name = service["serviceName"]
                                task_def_arn = service["taskDefinition"]
                                
                                # Extract family and revision from ARN
                                # Format: arn:aws:ecs:region:account:task-definition/family:revision
                                if "/task-definition/" in task_def_arn:
                                    family_revision = task_def_arn.split("/task-definition/")[-1]
                                    if ":" in family_revision:
                                        family, revision = family_revision.rsplit(":", 1)
                                        service_list[service_name] = {family: int(revision)}
                        except Exception as e:
                            logger.debug(f"Error describing services batch: {e}")
                            continue
            
            if service_list:
                cluster_details[cluster_name] = service_list
    
    return cluster_details


def _get_all_task_definition_revisions(ecs_client: Any, max_results: int) -> dict:
    """Get all task definition revisions (ACTIVE and INACTIVE)."""
    all_revisions = {}
    
    # Process ACTIVE task definitions
    active_paginator = ecs_client.get_paginator("list_task_definitions")
    for page in active_paginator.paginate(
        status="ACTIVE",
        PaginationConfig={"PageSize": max_results}
    ):
        for task_def_arn in page.get("taskDefinitionArns", []):
            # Parse ARN to extract family and revision
            # Format: arn:aws:ecs:region:account:task-definition/family:revision
            if "/task-definition/" in task_def_arn:
                family_revision = task_def_arn.split("/task-definition/")[-1]
                if ":" in family_revision:
                    family, revision = family_revision.rsplit(":", 1)
                    revision = int(revision)
                    
                    if family in all_revisions:
                        all_revisions[family].append(revision)
                    else:
                        all_revisions[family] = [revision]
    
    # Process INACTIVE task definitions
    inactive_paginator = ecs_client.get_paginator("list_task_definitions")
    for page in inactive_paginator.paginate(
        status="INACTIVE",
        PaginationConfig={"PageSize": max_results}
    ):
        for task_def_arn in page.get("taskDefinitionArns", []):
            # Parse ARN to extract family and revision
            if "/task-definition/" in task_def_arn:
                family_revision = task_def_arn.split("/task-definition/")[-1]
                if ":" in family_revision:
                    family, revision = family_revision.rsplit(":", 1)
                    revision = int(revision)
                    
                    if family in all_revisions:
                        all_revisions[family].append(revision)
                    else:
                        all_revisions[family] = [revision]
    
    return all_revisions


def find_unused_ecr_images(
    session: Any, region_name: str, period: int = 90, max_results: int = 100
) -> dict[str, Any]:
    """Find ECR images not pulled in the specified period.
    
    Args:
        session: Boto3 session
        region_name: AWS region name
        period: Lookback period in days
        max_results: Maximum results to return
    
    Returns:
        Dictionary with unused ECR images
    """
    ecr_client = session.client("ecr", region_name=region_name)
    
    cutoff_date = datetime.now() - timedelta(days=period)
    output_data = []
    
    logger.info(f"Finding unused ECR images in {region_name}")
    
    try:
        # Get all repositories
        repos_response = ecr_client.describe_repositories(maxResults=max_results)
        
        for repo in repos_response.get("repositories", []):
            repo_name = repo["repositoryName"]
            
            try:
                # Get images in repository
                images_response = ecr_client.describe_images(
                    repositoryName=repo_name,
                    maxResults=max_results
                )
                
                for image in images_response.get("imageDetails", []):
                    image_pushed_at = image.get("imagePushedAt")
                    last_pulled_at = image.get("lastRecordedPullTime")
                    
                    # Check if image hasn't been pulled recently
                    is_unused = False
                    if last_pulled_at:
                        if last_pulled_at < cutoff_date:
                            is_unused = True
                    elif image_pushed_at and image_pushed_at < cutoff_date:
                        # Never pulled and old
                        is_unused = True
                    
                    if is_unused:
                        image_digest = image.get("imageDigest", "N/A")
                        image_tags = image.get("imageTags", [])
                        image_size = image.get("imageSizeInBytes", 0)
                        image_size_mb = image_size / (1024 * 1024)
                        
                        # Calculate age
                        age_days = 0
                        if image_pushed_at:
                            age_days = (datetime.now(image_pushed_at.tzinfo) - image_pushed_at).days
                        
                        # ECR cost: $0.10/GB/month
                        monthly_cost = (image_size_mb / 1024) * 0.10
                        
                        output_data.append({
                            "RepositoryName": repo_name,
                            "ImageDigest": image_digest[:20] + "...",
                            "ImageTags": ", ".join(image_tags) if image_tags else "untagged",
                            "ImageSizeMB": f"{image_size_mb:.2f}",
                            "ImagePushedAt": image_pushed_at.strftime("%Y-%m-%d %H:%M:%S") if image_pushed_at else "N/A",
                            "LastPulledAt": last_pulled_at.strftime("%Y-%m-%d %H:%M:%S") if last_pulled_at else "Never",
                            "AgeDays": age_days,
                            "EstimatedMonthlyCost": f"${monthly_cost:.4f}",
                            "Description": f"ECR image not pulled in the last {period} days",
                        })
            
            except Exception as e:
                logger.debug(f"Error processing repository {repo_name}: {e}")
                continue
        
        # Calculate total potential savings
        total_monthly_cost = sum(
            float(img["EstimatedMonthlyCost"].replace("$", ""))
            for img in output_data
        )
        
        fields = {
            "1": "RepositoryName",
            "2": "ImageDigest",
            "3": "ImageTags",
            "4": "ImageSizeMB",
            "5": "ImagePushedAt",
            "6": "LastPulledAt",
            "7": "AgeDays",
            "8": "EstimatedMonthlyCost",
            "9": "Description",
        }
        
        return {
            "id": 208,
            "name": "Unused ECR Images",
            "fields": fields,
            "headers": fields_to_headers(fields),
            "count": len(output_data),
            "total_monthly_cost": f"${total_monthly_cost:.2f}",
            "resource": output_data,
        }
        
    except Exception as e:
        logger.error(f"Error finding unused ECR images: {e}")
        raise


def find_unused_launch_templates(
    session: Any, region_name: str, period: int = 90, max_results: int = 100
) -> dict[str, Any]:
    """Find launch templates not used by ASGs or EC2 instances.
    
    Args:
        session: Boto3 session
        region_name: AWS region name
        period: Minimum age in days
        max_results: Maximum results to return
    
    Returns:
        Dictionary with unused launch templates
    """
    ec2_client = session.client("ec2", region_name=region_name)
    asg_client = session.client("autoscaling", region_name=region_name)
    
    cutoff_date = datetime.now() - timedelta(days=period)
    output_data = []
    
    logger.info(f"Finding unused launch templates in {region_name}")
    
    try:
        # Get all launch templates
        templates_response = ec2_client.describe_launch_templates(MaxResults=max_results)
        
        # Get launch templates used by ASGs
        used_templates = set()
        asgs_response = asg_client.describe_auto_scaling_groups(MaxRecords=max_results)
        
        for asg in asgs_response.get("AutoScalingGroups", []):
            if "LaunchTemplate" in asg:
                used_templates.add(asg["LaunchTemplate"]["LaunchTemplateId"])
        
        # Check each launch template
        for template in templates_response.get("LaunchTemplates", []):
            template_id = template["LaunchTemplateId"]
            template_name = template["LaunchTemplateName"]
            create_time = template.get("CreateTime")
            
            # Skip if used by ASG
            if template_id in used_templates:
                continue
            
            # Check if old enough
            if create_time:
                age_days = (datetime.now(create_time.tzinfo) - create_time).days
                
                if age_days >= period:
                    # Check if used by any instances
                    instances_response = ec2_client.describe_instances(
                        Filters=[
                            {"Name": "instance-state-name", "Values": ["running", "stopped"]},
                        ],
                        MaxResults=max_results
                    )
                    
                    used_by_instance = False
                    for reservation in instances_response["Reservations"]:
                        for instance in reservation["Instances"]:
                            if instance.get("LaunchTemplate", {}).get("LaunchTemplateId") == template_id:
                                used_by_instance = True
                                break
                        if used_by_instance:
                            break
                    
                    if not used_by_instance:
                        # Get tags
                        tags = template.get("Tags", [])
                        tags_str = ", ".join([f"{tag['Key']}={tag['Value']}" for tag in tags]) if tags else "None"
                        
                        output_data.append({
                            "LaunchTemplateId": template_id,
                            "LaunchTemplateName": template_name,
                            "VersionNumber": template.get("LatestVersionNumber", 0),
                            "CreateTime": create_time.strftime("%Y-%m-%d %H:%M:%S"),
                            "AgeDays": age_days,
                            "CreatedBy": template.get("CreatedBy", "N/A"),
                            "DefaultVersion": template.get("DefaultVersionNumber", 0),
                            "LatestVersion": template.get("LatestVersionNumber", 0),
                            "Tags": tags_str,
                            "Description": f"Launch template not used by ASGs or instances for {period}+ days",
                        })
        
        fields = {
            "1": "LaunchTemplateId",
            "2": "LaunchTemplateName",
            "3": "VersionNumber",
            "4": "CreateTime",
            "5": "AgeDays",
            "6": "CreatedBy",
            "7": "DefaultVersion",
            "8": "LatestVersion",
            "9": "Tags",
            "10": "Description",
        }
        
        return {
            "id": 209,
            "name": "Unused Launch Templates",
            "fields": fields,
            "headers": fields_to_headers(fields),
            "count": len(output_data),
            "resource": output_data,
        }
        
    except Exception as e:
        logger.error(f"Error finding unused launch templates: {e}")
        raise



def find_unused_ecs_clusters_and_services(
    session: Any, region_name: str, period: int = 90
) -> dict[str, Any]:
    """Find ECS clusters and services with no activity in the specified period.
    
    This function identifies:
    - Clusters with no active services, tasks, or scheduled tasks
    - Services with zero running tasks and no recent CloudWatch activity
    
    Args:
        session: Boto3 session
        region_name: AWS region name
        period: Lookback period in days for activity check
    
    Returns:
        Dictionary with unused ECS clusters and services
    """
    ecs_client = session.client("ecs", region_name=region_name)
    cloudwatch_client = session.client("cloudwatch", region_name=region_name)
    events_client = session.client("events", region_name=region_name)
    
    output_data = []
    
    logger.info(f"Finding unused ECS clusters and services in {region_name}")
    
    try:
        # Get all clusters
        clusters_response = ecs_client.list_clusters()
        cluster_arns = clusters_response.get("clusterArns", [])
        
        if not cluster_arns:
            logger.info("No ECS clusters found")
            return {
                "id": 210,
                "name": "Unused ECS Clusters and Services",
                "fields": {},
                "headers": [],
                "count": 0,
                "resource": [],
            }
        
        for cluster_arn in cluster_arns:
            cluster_name = cluster_arn.split("/")[-1]
            
            # Get cluster details
            services_response = ecs_client.list_services(cluster=cluster_arn)
            service_arns = services_response.get("serviceArns", [])
            
            tasks_response = ecs_client.list_tasks(cluster=cluster_arn)
            task_arns = tasks_response.get("taskArns", [])
            
            container_instances_response = ecs_client.list_container_instances(cluster=cluster_arn)
            container_instance_arns = container_instances_response.get("containerInstanceArns", [])
            
            # Check for scheduled tasks via EventBridge
            scheduled_tasks = _list_scheduled_tasks_for_cluster(events_client, cluster_name)
            
            # If cluster has no services, tasks, container instances, or scheduled tasks
            if not service_arns and not task_arns and not container_instance_arns and not scheduled_tasks:
                output_data.append({
                    "ClusterName": cluster_name,
                    "ClusterStatus": "Inactive",
                    "ServiceName": "",
                    "ServiceStatus": "",
                    "RunningTasks": 0,
                    "DesiredTasks": 0,
                    "ScheduledTasks": 0,
                    "Description": f"Cluster has no active services, tasks, container instances, or scheduled tasks for past {period} days",
                })
                continue
            
            # If cluster has tasks or container instances, it's active
            if task_arns or container_instance_arns:
                # Cluster is active, skip to next cluster
                continue
            
            # Check each service
            if service_arns:
                # Describe services in batches of 10
                for i in range(0, len(service_arns), 10):
                    batch_service_arns = service_arns[i:i+10]
                    services_details = ecs_client.describe_services(
                        cluster=cluster_arn,
                        services=batch_service_arns
                    )
                    
                    for service in services_details.get("services", []):
                        service_name = service["serviceName"]
                        running_count = service.get("runningCount", 0)
                        desired_count = service.get("desiredCount", 0)
                        
                        # If service has zero running tasks
                        if running_count == 0:
                            # Check CloudWatch metrics for recent activity
                            has_recent_activity = _check_service_cloudwatch_activity(
                                cloudwatch_client, cluster_name, service_name, period
                            )
                            
                            if not has_recent_activity:
                                output_data.append({
                                    "ClusterName": cluster_name,
                                    "ClusterStatus": "Active",
                                    "ServiceName": service_name,
                                    "ServiceStatus": "Inactive",
                                    "RunningTasks": running_count,
                                    "DesiredTasks": desired_count,
                                    "ScheduledTasks": len(scheduled_tasks),
                                    "Description": f"Service has zero running tasks and no recent activity for past {period} days",
                                })
        
        fields = {
            "1": "ClusterName",
            "2": "ClusterStatus",
            "3": "ServiceName",
            "4": "ServiceStatus",
            "5": "RunningTasks",
            "6": "DesiredTasks",
            "7": "ScheduledTasks",
            "8": "Description",
        }
        
        return {
            "id": 210,
            "name": "Unused ECS Clusters and Services",
            "fields": fields,
            "headers": fields_to_headers(fields),
            "count": len(output_data),
            "resource": output_data,
        }
        
    except Exception as e:
        logger.error(f"Error finding unused ECS clusters and services: {e}")
        raise


def _list_scheduled_tasks_for_cluster(events_client: Any, cluster_name: str) -> list:
    """List EventBridge rules that schedule tasks for a specific ECS cluster."""
    scheduled_tasks = []
    
    try:
        # Get all EventBridge rules
        rules_response = events_client.list_rules()
        
        for rule in rules_response.get("Rules", []):
            rule_name = rule["Name"]
            
            # Get targets for this rule
            targets_response = events_client.list_targets_by_rule(Rule=rule_name)
            
            for target in targets_response.get("Targets", []):
                target_arn = target.get("Arn", "")
                
                # Check if target is an ECS task for this cluster
                if "arn:aws:ecs:" in target_arn and cluster_name in target_arn:
                    scheduled_tasks.append(rule_name)
                    break
    
    except Exception as e:
        logger.debug(f"Error listing scheduled tasks for cluster {cluster_name}: {e}")
    
    return scheduled_tasks


def _check_service_cloudwatch_activity(
    cloudwatch_client: Any, cluster_name: str, service_name: str, period: int
) -> bool:
    """Check if ECS service has recent CloudWatch activity."""
    start_time = datetime.now() - timedelta(days=period)
    end_time = datetime.now()
    
    try:
        # Check CPU utilization
        cpu_response = cloudwatch_client.get_metric_statistics(
            Namespace="AWS/ECS",
            MetricName="CPUUtilization",
            Dimensions=[
                {"Name": "ClusterName", "Value": cluster_name},
                {"Name": "ServiceName", "Value": service_name}
            ],
            StartTime=start_time,
            EndTime=end_time,
            Period=86400,  # Daily
            Statistics=["Maximum"]
        )
        
        if cpu_response.get("Datapoints"):
            max_cpu = max(point["Maximum"] for point in cpu_response["Datapoints"])
            if max_cpu > 0:
                return True
        
        # Check memory utilization
        memory_response = cloudwatch_client.get_metric_statistics(
            Namespace="AWS/ECS",
            MetricName="MemoryUtilization",
            Dimensions=[
                {"Name": "ClusterName", "Value": cluster_name},
                {"Name": "ServiceName", "Value": service_name}
            ],
            StartTime=start_time,
            EndTime=end_time,
            Period=86400,  # Daily
            Statistics=["Maximum"]
        )
        
        if memory_response.get("Datapoints"):
            max_memory = max(point["Maximum"] for point in memory_response["Datapoints"])
            if max_memory > 0:
                return True
    
    except Exception as e:
        logger.debug(f"Error checking CloudWatch activity for service {service_name}: {e}")
    
    return False
