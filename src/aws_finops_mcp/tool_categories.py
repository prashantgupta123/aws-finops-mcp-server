"""Tool category definitions for AWS FinOps MCP Server."""

# Define tool categories and their associated tool names
TOOL_CATEGORIES = {
    "cleanup": [
        "find_unused_lambda_functions",
        "find_unused_elastic_ips",
        "find_unused_amis",
        "find_unused_load_balancers",
        "find_unused_target_groups",
        "find_unused_log_groups",
        "find_unused_snapshots",
        "find_unused_security_groups",
        "find_unused_volumes",
    ],
    "capacity": [
        "find_underutilized_ec2_instances",
        "find_overutilized_ec2_instances",
        "find_underutilized_rds_instances",
        "find_overutilized_rds_instances",
        "find_overutilized_dynamodb_tables",
        "find_underutilized_elasticache_clusters",
        "find_overutilized_elasticache_clusters",
        "find_underutilized_ecs_services",
        "find_underutilized_lambda_functions",
    ],
    "cost": [
        "get_all_cost_optimization_recommendations",
        "get_cost_optimization_ec2",
        "get_cost_optimization_lambda",
        "get_cost_optimization_rds",
        "get_cost_optimization_ebs",
        "get_cost_by_region",
        "get_cost_by_service",
        "get_cost_by_region_and_service",
        "get_daily_cost_trend",
        "get_savings_plans_recommendations",
        "get_reserved_instance_recommendations",
        "analyze_reserved_instance_utilization",
        "get_ebs_volume_type_recommendations",
        "get_snapshot_lifecycle_recommendations",
        "analyze_data_transfer_costs",
        "get_nat_gateway_optimization_recommendations",
    ],
    "application": [
        "find_target_groups_with_high_error_rate",
        "find_target_groups_with_high_response_time",
    ],
    "upgrade": [
        "find_asgs_with_old_amis",
        "find_outdated_rds_engine_versions",
        "find_outdated_elasticache_engine_versions",
        "find_outdated_lambda_runtimes",
        "find_ec2_instances_with_old_generations",
        "find_ebs_volumes_with_old_types",
        "find_outdated_ecs_platform_versions",
        "find_outdated_eks_cluster_versions",
    ],
    "network": [
        "find_unused_nat_gateways",
        "find_unused_vpc_endpoints",
        "find_unused_internet_gateways",
        "find_unused_cloudfront_distributions",
        "find_unused_route53_hosted_zones",
    ],
    "storage": [
        "find_unused_s3_buckets",
        "get_s3_storage_class_recommendations",
    ],
    "containers": [
        "find_old_ecs_task_definitions",
        "find_unused_ecr_images",
        "find_unused_launch_templates",
        "find_unused_ecs_clusters_and_services",
    ],
    "messaging": [
        "find_unused_sqs_queues",
        "find_unused_sns_topics",
        "find_unused_eventbridge_rules",
    ],
    "database": [
        "find_unused_dynamodb_tables",
        "find_underutilized_dynamodb_tables",
    ],
    "monitoring": [
        "find_unused_cloudwatch_alarms",
        "find_orphaned_cloudwatch_dashboards",
        "find_orphaned_cloudwatch_alarms",
    ],
    "performance": [
        "analyze_lambda_cold_starts",
        "analyze_api_gateway_performance",
        "analyze_dynamodb_throttling",
        "analyze_rds_performance_insights",
        "analyze_cloudfront_cache_hit_ratio",
    ],
    "security": [
        "find_unencrypted_ebs_volumes",
        "find_unencrypted_s3_buckets",
        "find_unencrypted_rds_instances",
        "find_public_s3_buckets",
        "find_overly_permissive_security_groups",
    ],
    "governance": [
        "find_untagged_resources",
        "analyze_tag_compliance",
        "generate_cost_allocation_report",
    ],
}


def get_enabled_categories(categories_env: str | None = None) -> set[str]:
    """
    Parse enabled categories from environment variable.
    
    Args:
        categories_env: Comma-separated list of categories or "all"
        
    Returns:
        Set of enabled category names
    """
    if not categories_env or categories_env.strip().lower() == "all":
        return set(TOOL_CATEGORIES.keys())
    
    # Parse comma-separated categories
    enabled = {cat.strip().lower() for cat in categories_env.split(",") if cat.strip()}
    
    # Validate categories
    valid_categories = set(TOOL_CATEGORIES.keys())
    invalid = enabled - valid_categories
    if invalid:
        raise ValueError(
            f"Invalid categories: {invalid}. "
            f"Valid categories are: {', '.join(sorted(valid_categories))}"
        )
    
    return enabled


def get_enabled_tools(categories_env: str | None = None) -> set[str]:
    """
    Get set of enabled tool names based on categories.
    
    Args:
        categories_env: Comma-separated list of categories or "all"
        
    Returns:
        Set of enabled tool names
    """
    enabled_categories = get_enabled_categories(categories_env)
    enabled_tools = set()
    
    for category in enabled_categories:
        enabled_tools.update(TOOL_CATEGORIES[category])
    
    return enabled_tools


def is_tool_enabled(tool_name: str, categories_env: str | None = None) -> bool:
    """
    Check if a specific tool is enabled based on categories.
    
    Args:
        tool_name: Name of the tool to check
        categories_env: Comma-separated list of categories or "all"
        
    Returns:
        True if tool is enabled, False otherwise
    """
    enabled_tools = get_enabled_tools(categories_env)
    return tool_name in enabled_tools
