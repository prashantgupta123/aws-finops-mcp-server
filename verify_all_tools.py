#!/usr/bin/env python3
"""Verify all 74 AWS FinOps MCP tools are properly registered."""

from src.aws_finops_mcp.server import mcp

# Expected tool categories and counts
EXPECTED_TOOLS = {
    "Cleanup": [
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
    "Capacity": [
        "find_underutilized_ec2_instances",
        "find_overutilized_ec2_instances",
        "find_underutilized_rds_instances",
        "find_overutilized_rds_instances",
    ],
    "Cost Optimization": [
        "get_all_cost_optimization_recommendations",
        "get_cost_optimization_ec2",
        "get_cost_optimization_lambda",
        "get_cost_optimization_rds",
        "get_cost_optimization_ebs",
    ],
    "Application": [
        "find_target_groups_with_high_error_rate",
        "find_target_groups_with_high_response_time",
    ],
    "Cost Explorer": [
        "get_cost_by_region",
        "get_cost_by_service",
        "get_cost_by_region_and_service",
        "get_daily_cost_trend",
    ],
    "Upgrade": [
        "find_asgs_with_old_amis",
    ],
    "Network": [
        "find_unused_nat_gateways",
        "find_unused_vpc_endpoints",
        "find_unused_internet_gateways",
        "find_unused_cloudfront_distributions",
        "find_unused_route53_hosted_zones",
    ],
    "Storage": [
        "find_unused_s3_buckets",
        "get_s3_storage_class_recommendations",
    ],
    "Containers": [
        "find_old_ecs_task_definitions",
        "find_unused_ecr_images",
        "find_unused_launch_templates",
    ],
    "Messaging": [
        "find_unused_sqs_queues",
        "find_unused_sns_topics",
        "find_unused_eventbridge_rules",
    ],
    "Database": [
        "find_unused_dynamodb_tables",
        "find_underutilized_dynamodb_tables",
    ],
    "Monitoring": [
        "find_unused_cloudwatch_alarms",
        "find_orphaned_cloudwatch_dashboards",
    ],
    "Capacity Database": [
        "find_overutilized_dynamodb_tables",
        "find_underutilized_elasticache_clusters",
        "find_overutilized_elasticache_clusters",
        "find_underutilized_ecs_services",
    ],
    "Capacity Compute": [
        "find_underutilized_lambda_functions",
    ],
    "Cost Savings": [
        "get_savings_plans_recommendations",
        "get_reserved_instance_recommendations",
        "analyze_reserved_instance_utilization",
    ],
    "Cost Storage": [
        "get_ebs_volume_type_recommendations",
        "get_snapshot_lifecycle_recommendations",
    ],
    "Cost Network": [
        "analyze_data_transfer_costs",
        "get_nat_gateway_optimization_recommendations",
    ],
    "Upgrade Database": [
        "find_outdated_rds_engine_versions",
        "find_outdated_elasticache_engine_versions",
    ],
    "Upgrade Compute": [
        "find_outdated_lambda_runtimes",
        "find_ec2_instances_with_old_generations",
        "find_ebs_volumes_with_old_types",
        "find_outdated_ecs_platform_versions",
    ],
    "Upgrade Containers": [
        "find_outdated_eks_cluster_versions",
    ],
    "Performance": [
        "analyze_lambda_cold_starts",
        "analyze_api_gateway_performance",
        "analyze_dynamodb_throttling",
        "analyze_rds_performance_insights",
        "analyze_cloudfront_cache_hit_ratio",
    ],
    "Security": [
        "find_unencrypted_ebs_volumes",
        "find_unencrypted_s3_buckets",
        "find_unencrypted_rds_instances",
        "find_public_s3_buckets",
        "find_overly_permissive_security_groups",
    ],
    "Governance": [
        "find_untagged_resources",
        "analyze_tag_compliance",
        "generate_cost_allocation_report",
    ],
}

def main():
    """Verify all tools are registered."""
    # Get registered tools
    registered_tools = set(mcp._tool_manager._tools.keys())
    
    # Flatten expected tools
    expected_tools = set()
    for category, tools in EXPECTED_TOOLS.items():
        expected_tools.update(tools)
    
    # Calculate totals
    total_expected = len(expected_tools)
    total_registered = len(registered_tools)
    
    print("=" * 80)
    print("AWS FinOps MCP Server - Tool Verification")
    print("=" * 80)
    print(f"\n✓ Expected tools: {total_expected}")
    print(f"✓ Registered tools: {total_registered}")
    
    # Check for missing tools
    missing_tools = expected_tools - registered_tools
    if missing_tools:
        print(f"\n❌ MISSING TOOLS ({len(missing_tools)}):")
        for tool in sorted(missing_tools):
            print(f"   - {tool}")
    else:
        print("\n✓ All expected tools are registered!")
    
    # Check for extra tools
    extra_tools = registered_tools - expected_tools
    if extra_tools:
        print(f"\n⚠️  EXTRA TOOLS ({len(extra_tools)}):")
        for tool in sorted(extra_tools):
            print(f"   - {tool}")
    
    # Print by category
    print("\n" + "=" * 80)
    print("Tools by Category")
    print("=" * 80)
    
    for category, tools in EXPECTED_TOOLS.items():
        print(f"\n{category} ({len(tools)} tools):")
        for tool in tools:
            status = "✓" if tool in registered_tools else "❌"
            print(f"  {status} {tool}")
    
    # Summary
    print("\n" + "=" * 80)
    print("Summary")
    print("=" * 80)
    print(f"Categories: {len(EXPECTED_TOOLS)}")
    print(f"Expected tools: {total_expected}")
    print(f"Registered tools: {total_registered}")
    print(f"Missing: {len(missing_tools)}")
    print(f"Extra: {len(extra_tools)}")
    
    if missing_tools or total_registered != total_expected:
        print("\n❌ VERIFICATION FAILED")
        return 1
    else:
        print("\n✅ VERIFICATION PASSED - All tools registered successfully!")
        return 0

if __name__ == "__main__":
    exit(main())
