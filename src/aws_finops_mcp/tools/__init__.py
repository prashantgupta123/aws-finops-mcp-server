"""AWS FinOps tools modules."""

# Existing tools - import modules for backward compatibility
from . import cleanup
from . import capacity
from . import cost
from . import cost_explorer
from . import application
from . import upgrade

# New network tools
from .network import (
    find_unused_nat_gateways,
    find_unused_vpc_endpoints,
    find_unused_internet_gateways,
    find_unused_cloudfront_distributions,
    find_unused_route53_hosted_zones,
)

# New storage tools
from .storage import (
    find_unused_s3_buckets,
    get_s3_storage_class_recommendations,
)

# New container tools
from .containers import (
    find_old_ecs_task_definitions,
    find_unused_ecr_images,
    find_unused_launch_templates,
)

# New messaging tools
from .messaging import (
    find_unused_sqs_queues,
    find_unused_sns_topics,
    find_unused_eventbridge_rules,
)

# New database tools
from .database import (
    find_unused_dynamodb_tables,
    find_underutilized_dynamodb_tables,
)

# New monitoring tools
from .monitoring import (
    find_unused_cloudwatch_alarms,
    find_orphaned_cloudwatch_dashboards,
)

# New capacity database tools
from .capacity_database import (
    find_overutilized_dynamodb_tables,
    find_underutilized_elasticache_clusters,
    find_overutilized_elasticache_clusters,
    find_underutilized_ecs_services,
)

# New capacity compute tools
from .capacity_compute import (
    find_underutilized_lambda_functions,
)

# New cost savings tools
from .cost_savings import (
    get_savings_plans_recommendations,
    get_reserved_instance_recommendations,
    analyze_reserved_instance_utilization,
)

# New cost storage tools
from .cost_storage import (
    get_ebs_volume_type_recommendations,
    get_snapshot_lifecycle_recommendations,
)

# New cost network tools
from .cost_network import (
    analyze_data_transfer_costs,
    get_nat_gateway_optimization_recommendations,
)

# New upgrade database tools
from .upgrade_database import (
    find_outdated_rds_engine_versions,
    find_outdated_elasticache_engine_versions,
)

# New upgrade compute tools
from .upgrade_compute import (
    find_outdated_lambda_runtimes,
    find_ec2_instances_with_old_generations,
    find_ebs_volumes_with_old_types,
    find_outdated_ecs_platform_versions,
)

# New upgrade containers tools
from .upgrade_containers import (
    find_outdated_eks_cluster_versions,
)

# New performance tools
from .performance import (
    analyze_lambda_cold_starts,
    analyze_api_gateway_performance,
    analyze_dynamodb_throttling,
    analyze_rds_performance_insights,
    analyze_cloudfront_cache_hit_ratio,
)

# New security tools
from .security import (
    find_unencrypted_ebs_volumes,
    find_unencrypted_s3_buckets,
    find_unencrypted_rds_instances,
    find_public_s3_buckets,
    find_overly_permissive_security_groups,
)

# New governance tools
from .governance import (
    find_untagged_resources,
    analyze_tag_compliance,
    generate_cost_allocation_report,
)

# Import new modules for server.py
from . import network
from . import storage
from . import containers
from . import messaging
from . import database
from . import monitoring
from . import capacity_database
from . import capacity_compute
from . import cost_savings
from . import cost_storage
from . import cost_network
from . import upgrade_database
from . import upgrade_compute
from . import upgrade_containers
from . import performance
from . import security
from . import governance

__all__ = [
    # Existing modules
    "cleanup",
    "capacity",
    "cost",
    "cost_explorer",
    "application",
    "upgrade",
    # New modules
    "network",
    "storage",
    "containers",
    "messaging",
    "database",
    "monitoring",
    "capacity_database",
    "capacity_compute",
    "cost_savings",
    "cost_storage",
    "cost_network",
    "upgrade_database",
    "upgrade_compute",
    "upgrade_containers",
    "performance",
    "security",
    "governance",
    # New network tools
    "find_unused_nat_gateways",
    "find_unused_vpc_endpoints",
    "find_unused_internet_gateways",
    "find_unused_cloudfront_distributions",
    "find_unused_route53_hosted_zones",
    # New storage tools
    "find_unused_s3_buckets",
    "get_s3_storage_class_recommendations",
    # New container tools
    "find_old_ecs_task_definitions",
    "find_unused_ecr_images",
    "find_unused_launch_templates",
    # New messaging tools
    "find_unused_sqs_queues",
    "find_unused_sns_topics",
    "find_unused_eventbridge_rules",
    # New database tools
    "find_unused_dynamodb_tables",
    "find_underutilized_dynamodb_tables",
    # New monitoring tools
    "find_unused_cloudwatch_alarms",
    "find_orphaned_cloudwatch_dashboards",
    # New capacity database tools
    "find_overutilized_dynamodb_tables",
    "find_underutilized_elasticache_clusters",
    "find_overutilized_elasticache_clusters",
    "find_underutilized_ecs_services",
    # New capacity compute tools
    "find_underutilized_lambda_functions",
    # New cost savings tools
    "get_savings_plans_recommendations",
    "get_reserved_instance_recommendations",
    "analyze_reserved_instance_utilization",
    # New cost storage tools
    "get_ebs_volume_type_recommendations",
    "get_snapshot_lifecycle_recommendations",
    # New cost network tools
    "analyze_data_transfer_costs",
    "get_nat_gateway_optimization_recommendations",
    # New upgrade database tools
    "find_outdated_rds_engine_versions",
    "find_outdated_elasticache_engine_versions",
    # New upgrade compute tools
    "find_outdated_lambda_runtimes",
    "find_ec2_instances_with_old_generations",
    "find_ebs_volumes_with_old_types",
    "find_outdated_ecs_platform_versions",
    # New upgrade containers tools
    "find_outdated_eks_cluster_versions",
    # New performance tools
    "analyze_lambda_cold_starts",
    "analyze_api_gateway_performance",
    "analyze_dynamodb_throttling",
    "analyze_rds_performance_insights",
    "analyze_cloudfront_cache_hit_ratio",
    # New security tools
    "find_unencrypted_ebs_volumes",
    "find_unencrypted_s3_buckets",
    "find_unencrypted_rds_instances",
    "find_public_s3_buckets",
    "find_overly_permissive_security_groups",
    # New governance tools
    "find_untagged_resources",
    "analyze_tag_compliance",
    "generate_cost_allocation_report",
]
