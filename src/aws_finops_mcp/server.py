"""AWS FinOps MCP Server - FastMCP implementation."""

import logging
from typing import Any

from mcp.server.fastmcp import FastMCP

from .session import get_aws_session
from .tools import (
    cleanup, capacity, cost, application, upgrade, cost_explorer,
    network, storage, containers, messaging, database, monitoring,
    capacity_database, capacity_compute, cost_savings, cost_storage, cost_network,
    upgrade_database, upgrade_compute, upgrade_containers,
    performance, security, governance
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("aws-finops")


# Helper function to create session from credentials
def create_session(
    profile_name: str | None = None,
    role_arn: str | None = None,
    access_key: str | None = None,
    secret_access_key: str | None = None,
    session_token: str | None = None,
    region_name: str = "us-east-1",
) -> Any:
    """Create AWS session from provided credentials."""
    return get_aws_session(
        profile_name=profile_name,
        role_arn=role_arn,
        access_key=access_key,
        secret_access_key=secret_access_key,
        session_token=session_token,
        region_name=region_name,
    )


# ============================================================================
# CLEANUP TOOLS
# ============================================================================

@mcp.tool()
def find_unused_lambda_functions(
    region_name: str = "us-east-1",
    period: int = 90,
    max_results: int = 100,
    profile_name: str | None = None,
    role_arn: str | None = None,
    access_key: str | None = None,
    secret_access_key: str | None = None,
    session_token: str | None = None,
) -> dict[str, Any]:
    """Find Lambda functions with no invocations in the specified period.
    
    Args:
        region_name: AWS region name
        period: Lookback period in days (default: 90)
        max_results: Maximum results to return (default: 100)
        profile_name: AWS profile name (optional)
        role_arn: IAM role ARN to assume (optional)
        access_key: AWS access key ID (optional)
        secret_access_key: AWS secret access key (optional)
        session_token: AWS session token for temporary credentials (optional)
    
    Returns:
        Dictionary with unused Lambda functions
    """
    session = create_session(profile_name, role_arn, access_key, secret_access_key, session_token, region_name)
    return cleanup.find_unused_lambda_functions(session, region_name, period, max_results)


@mcp.tool()
def find_unused_elastic_ips(
    region_name: str = "us-east-1",
    profile_name: str | None = None,
    role_arn: str | None = None,
    access_key: str | None = None,
    secret_access_key: str | None = None,
    session_token: str | None = None,
) -> dict[str, Any]:
    """Find unattached Elastic IPs.
    
    Args:
        region_name: AWS region name
        profile_name: AWS profile name (optional)
        role_arn: IAM role ARN to assume (optional)
        access_key: AWS access key ID (optional)
        secret_access_key: AWS secret access key (optional)
        session_token: AWS session token for temporary credentials (optional)
    
    Returns:
        Dictionary with unused Elastic IPs
    """
    session = create_session(profile_name, role_arn, access_key, secret_access_key, session_token, region_name)
    return cleanup.find_unused_elastic_ips(session, region_name)


@mcp.tool()
def find_unused_amis(
    region_name: str = "us-east-1",
    period: int = 90,
    max_results: int = 100,
    profile_name: str | None = None,
    role_arn: str | None = None,
    access_key: str | None = None,
    secret_access_key: str | None = None,
    session_token: str | None = None,
) -> dict[str, Any]:
    """Find AMIs not used by any EC2 instances, ASGs, or Spot Fleet Requests.
    
    Args:
        region_name: AWS region name
        period: Minimum age in days for AMI to be considered unused (default: 90)
        max_results: Maximum results to return (default: 100)
        profile_name: AWS profile name (optional)
        role_arn: IAM role ARN to assume (optional)
        access_key: AWS access key ID (optional)
        secret_access_key: AWS secret access key (optional)
        session_token: AWS session token for temporary credentials (optional)
    
    Returns:
        Dictionary with unused AMIs
    """
    session = create_session(profile_name, role_arn, access_key, secret_access_key, session_token, region_name)
    return cleanup.find_unused_amis(session, region_name, period, max_results)


@mcp.tool()
def find_unused_load_balancers(
    region_name: str = "us-east-1",
    period: int = 90,
    profile_name: str | None = None,
    role_arn: str | None = None,
    access_key: str | None = None,
    secret_access_key: str | None = None,
    session_token: str | None = None,
) -> dict[str, Any]:
    """Find load balancers with no traffic in the specified period.
    
    Args:
        region_name: AWS region name
        period: Lookback period in days (default: 90)
        profile_name: AWS profile name (optional)
        role_arn: IAM role ARN to assume (optional)
        access_key: AWS access key ID (optional)
        secret_access_key: AWS secret access key (optional)
        session_token: AWS session token for temporary credentials (optional)
    
    Returns:
        Dictionary with unused load balancers
    """
    session = create_session(profile_name, role_arn, access_key, secret_access_key, session_token, region_name)
    return cleanup.find_unused_load_balancers(session, region_name, period)


@mcp.tool()
def find_unused_target_groups(
    region_name: str = "us-east-1",
    period: int = 7,
    max_results: int = 100,
    profile_name: str | None = None,
    role_arn: str | None = None,
    access_key: str | None = None,
    secret_access_key: str | None = None,
    session_token: str | None = None,
) -> dict[str, Any]:
    """Find target groups with no registered targets or no traffic.
    
    This function identifies target groups that are:
    1. Not attached to any load balancer, OR
    2. Have no registered targets, OR
    3. Have registered targets but no traffic in the specified period
    
    Args:
        region_name: AWS region name
        period: Lookback period in days for traffic check (default: 7)
        max_results: Maximum results to return (default: 100)
        profile_name: AWS profile name (optional)
        role_arn: IAM role ARN to assume (optional)
        access_key: AWS access key ID (optional)
        secret_access_key: AWS secret access key (optional)
        session_token: AWS session token for temporary credentials (optional)
    
    Returns:
        Dictionary with unused target groups
    """
    session = create_session(profile_name, role_arn, access_key, secret_access_key, session_token, region_name)
    return cleanup.find_unused_target_groups(session, region_name, period, max_results)


@mcp.tool()
def find_unused_log_groups(
    region_name: str = "us-east-1",
    period: int = 90,
    max_results: int = 50,
    profile_name: str | None = None,
    role_arn: str | None = None,
    access_key: str | None = None,
    secret_access_key: str | None = None,
    session_token: str | None = None,
) -> dict[str, Any]:
    """Find CloudWatch Log Groups with no recent log events.
    
    Args:
        region_name: AWS region name
        period: Lookback period in days (default: 90)
        max_results: Maximum results to return (default: 50)
        profile_name: AWS profile name (optional)
        role_arn: IAM role ARN to assume (optional)
        access_key: AWS access key ID (optional)
        secret_access_key: AWS secret access key (optional)
        session_token: AWS session token for temporary credentials (optional)
    
    Returns:
        Dictionary with unused log groups
    """
    session = create_session(profile_name, role_arn, access_key, secret_access_key, session_token, region_name)
    return cleanup.find_unused_log_groups(session, region_name, period, max_results)


@mcp.tool()
def find_unused_snapshots(
    region_name: str = "us-east-1",
    period: int = 90,
    max_results: int = 100,
    profile_name: str | None = None,
    role_arn: str | None = None,
    access_key: str | None = None,
    secret_access_key: str | None = None,
    session_token: str | None = None,
) -> dict[str, Any]:
    """Find EBS snapshots not associated with any AMI or volume.
    
    Args:
        region_name: AWS region name
        period: Minimum age in days for snapshot to be considered unused (default: 90)
        max_results: Maximum results to return (default: 100)
        profile_name: AWS profile name (optional)
        role_arn: IAM role ARN to assume (optional)
        access_key: AWS access key ID (optional)
        secret_access_key: AWS secret access key (optional)
        session_token: AWS session token for temporary credentials (optional)
    
    Returns:
        Dictionary with unused snapshots
    """
    session = create_session(profile_name, role_arn, access_key, secret_access_key, session_token, region_name)
    return cleanup.find_unused_snapshots(session, region_name, period, max_results)


@mcp.tool()
def find_unused_security_groups(
    region_name: str = "us-east-1",
    max_results: int = 100,
    profile_name: str | None = None,
    role_arn: str | None = None,
    access_key: str | None = None,
    secret_access_key: str | None = None,
    session_token: str | None = None,
) -> dict[str, Any]:
    """Find security groups not attached to any resources.
    
    Args:
        region_name: AWS region name
        max_results: Maximum results to return (default: 100)
        profile_name: AWS profile name (optional)
        role_arn: IAM role ARN to assume (optional)
        access_key: AWS access key ID (optional)
        secret_access_key: AWS secret access key (optional)
        session_token: AWS session token for temporary credentials (optional)
    
    Returns:
        Dictionary with unused security groups
    """
    session = create_session(profile_name, role_arn, access_key, secret_access_key, session_token, region_name)
    return cleanup.find_unused_security_groups(session, region_name, max_results)


@mcp.tool()
def find_unused_volumes(
    region_name: str = "us-east-1",
    max_results: int = 100,
    profile_name: str | None = None,
    role_arn: str | None = None,
    access_key: str | None = None,
    secret_access_key: str | None = None,
    session_token: str | None = None,
) -> dict[str, Any]:
    """Find EBS volumes that are not attached to any instance.
    
    Args:
        region_name: AWS region name
        max_results: Maximum results to return (default: 100)
        profile_name: AWS profile name (optional)
        role_arn: IAM role ARN to assume (optional)
        access_key: AWS access key ID (optional)
        secret_access_key: AWS secret access key (optional)
        session_token: AWS session token for temporary credentials (optional)
    
    Returns:
        Dictionary with unused EBS volumes
    """
    session = create_session(profile_name, role_arn, access_key, secret_access_key, session_token, region_name)
    return cleanup.find_unused_volumes(session, region_name, max_results)



# ============================================================================
# CAPACITY TOOLS
# ============================================================================

@mcp.tool()
def find_underutilized_ec2_instances(
    region_name: str = "us-east-1",
    period: int = 30,
    max_results: int = 100,
    profile_name: str | None = None,
    role_arn: str | None = None,
    access_key: str | None = None,
    secret_access_key: str | None = None,
    session_token: str | None = None,
) -> dict[str, Any]:
    """Find EC2 instances with low CPU and memory utilization (≤20%).
    
    Args:
        region_name: AWS region name
        period: Lookback period in days (default: 30)
        max_results: Maximum results to return (default: 100)
        profile_name: AWS profile name (optional)
        role_arn: IAM role ARN to assume (optional)
        access_key: AWS access key ID (optional)
        secret_access_key: AWS secret access key (optional)
        session_token: AWS session token for temporary credentials (optional)
    
    Returns:
        Dictionary with underutilized EC2 instances
    """
    session = create_session(profile_name, role_arn, access_key, secret_access_key, session_token, region_name)
    return capacity.find_underutilized_ec2_instances(session, region_name, period, max_results)


@mcp.tool()
def find_overutilized_ec2_instances(
    region_name: str = "us-east-1",
    period: int = 30,
    max_results: int = 100,
    profile_name: str | None = None,
    role_arn: str | None = None,
    access_key: str | None = None,
    secret_access_key: str | None = None,
    session_token: str | None = None,
) -> dict[str, Any]:
    """Find EC2 instances with high CPU or memory utilization (≥80%).
    
    Args:
        region_name: AWS region name
        period: Lookback period in days (default: 30)
        max_results: Maximum results to return (default: 100)
        profile_name: AWS profile name (optional)
        role_arn: IAM role ARN to assume (optional)
        access_key: AWS access key ID (optional)
        secret_access_key: AWS secret access key (optional)
        session_token: AWS session token for temporary credentials (optional)
    
    Returns:
        Dictionary with overutilized EC2 instances
    """
    session = create_session(profile_name, role_arn, access_key, secret_access_key, session_token, region_name)
    return capacity.find_overutilized_ec2_instances(session, region_name, period, max_results)


@mcp.tool()
def find_underutilized_rds_instances(
    region_name: str = "us-east-1",
    period: int = 30,
    max_results: int = 100,
    profile_name: str | None = None,
    role_arn: str | None = None,
    access_key: str | None = None,
    secret_access_key: str | None = None,
    session_token: str | None = None,
) -> dict[str, Any]:
    """Find RDS instances with low CPU utilization (≤20%).
    
    Args:
        region_name: AWS region name
        period: Lookback period in days (default: 30)
        max_results: Maximum results to return (default: 100)
        profile_name: AWS profile name (optional)
        role_arn: IAM role ARN to assume (optional)
        access_key: AWS access key ID (optional)
        secret_access_key: AWS secret access key (optional)
        session_token: AWS session token for temporary credentials (optional)
    
    Returns:
        Dictionary with underutilized RDS instances
    """
    session = create_session(profile_name, role_arn, access_key, secret_access_key, session_token, region_name)
    return capacity.find_underutilized_rds_instances(session, region_name, period, max_results)


@mcp.tool()
def find_overutilized_rds_instances(
    region_name: str = "us-east-1",
    period: int = 30,
    max_results: int = 100,
    profile_name: str | None = None,
    role_arn: str | None = None,
    access_key: str | None = None,
    secret_access_key: str | None = None,
    session_token: str | None = None,
) -> dict[str, Any]:
    """Find RDS instances with high CPU utilization (≥80%).
    
    Args:
        region_name: AWS region name
        period: Lookback period in days (default: 30)
        max_results: Maximum results to return (default: 100)
        profile_name: AWS profile name (optional)
        role_arn: IAM role ARN to assume (optional)
        access_key: AWS access key ID (optional)
        secret_access_key: AWS secret access key (optional)
        session_token: AWS session token for temporary credentials (optional)
    
    Returns:
        Dictionary with overutilized RDS instances
    """
    session = create_session(profile_name, role_arn, access_key, secret_access_key, session_token, region_name)
    return capacity.find_overutilized_rds_instances(session, region_name, period, max_results)


# ============================================================================
# COST OPTIMIZATION TOOLS
# ============================================================================

@mcp.tool()
def get_all_cost_optimization_recommendations(
    region_name: str | None = None,
    profile_name: str | None = None,
    role_arn: str | None = None,
    access_key: str | None = None,
    secret_access_key: str | None = None,
    session_token: str | None = None,
) -> list[dict[str, Any]]:
    """Get all cost optimization recommendations from AWS Cost Optimization Hub.
    
    Returns recommendations for all resource types (19 types total).
    
    Args:
        region_name: AWS region to filter recommendations (optional)
        profile_name: AWS profile name (optional)
        role_arn: IAM role ARN to assume (optional)
        access_key: AWS access key ID (optional)
        secret_access_key: AWS secret access key (optional)
        session_token: AWS session token for temporary credentials (optional)
    
    Returns:
        List of dictionaries with cost optimization recommendations by resource type
    """
    session = create_session(profile_name, role_arn, access_key, secret_access_key, session_token, "us-east-1")
    return cost.get_cost_optimization_recommendations(session, region_name)


@mcp.tool()
def get_cost_optimization_ec2(
    region_name: str | None = None,
    profile_name: str | None = None,
    role_arn: str | None = None,
    access_key: str | None = None,
    secret_access_key: str | None = None,
    session_token: str | None = None,
) -> dict[str, Any]:
    """Get EC2 instance cost optimization recommendations.
    
    Args:
        region_name: AWS region to filter recommendations (optional)
        profile_name: AWS profile name (optional)
        role_arn: IAM role ARN to assume (optional)
        access_key: AWS access key ID (optional)
        secret_access_key: AWS secret access key (optional)
        session_token: AWS session token for temporary credentials (optional)
    
    Returns:
        Dictionary with EC2 cost optimization recommendations
    """
    session = create_session(profile_name, role_arn, access_key, secret_access_key, session_token, "us-east-1")
    return cost.get_cost_optimization_recommendations(session, region_name, "Ec2Instance")


@mcp.tool()
def get_cost_optimization_lambda(
    region_name: str | None = None,
    profile_name: str | None = None,
    role_arn: str | None = None,
    access_key: str | None = None,
    secret_access_key: str | None = None,
    session_token: str | None = None,
) -> dict[str, Any]:
    """Get Lambda function cost optimization recommendations.
    
    Args:
        region_name: AWS region to filter recommendations (optional)
        profile_name: AWS profile name (optional)
        role_arn: IAM role ARN to assume (optional)
        access_key: AWS access key ID (optional)
        secret_access_key: AWS secret access key (optional)
        session_token: AWS session token for temporary credentials (optional)
    
    Returns:
        Dictionary with Lambda cost optimization recommendations
    """
    session = create_session(profile_name, role_arn, access_key, secret_access_key, session_token, "us-east-1")
    return cost.get_cost_optimization_recommendations(session, region_name, "LambdaFunction")


@mcp.tool()
def get_cost_optimization_rds(
    region_name: str | None = None,
    profile_name: str | None = None,
    role_arn: str | None = None,
    access_key: str | None = None,
    secret_access_key: str | None = None,
    session_token: str | None = None,
) -> dict[str, Any]:
    """Get RDS instance cost optimization recommendations.
    
    Args:
        region_name: AWS region to filter recommendations (optional)
        profile_name: AWS profile name (optional)
        role_arn: IAM role ARN to assume (optional)
        access_key: AWS access key ID (optional)
        secret_access_key: AWS secret access key (optional)
        session_token: AWS session token for temporary credentials (optional)
    
    Returns:
        Dictionary with RDS cost optimization recommendations
    """
    session = create_session(profile_name, role_arn, access_key, secret_access_key, session_token, "us-east-1")
    return cost.get_cost_optimization_recommendations(session, region_name, "RdsDbInstance")


@mcp.tool()
def get_cost_optimization_ebs(
    region_name: str | None = None,
    profile_name: str | None = None,
    role_arn: str | None = None,
    access_key: str | None = None,
    secret_access_key: str | None = None,
    session_token: str | None = None,
) -> dict[str, Any]:
    """Get EBS volume cost optimization recommendations.
    
    Args:
        region_name: AWS region to filter recommendations (optional)
        profile_name: AWS profile name (optional)
        role_arn: IAM role ARN to assume (optional)
        access_key: AWS access key ID (optional)
        secret_access_key: AWS secret access key (optional)
        session_token: AWS session token for temporary credentials (optional)
    
    Returns:
        Dictionary with EBS cost optimization recommendations
    """
    session = create_session(profile_name, role_arn, access_key, secret_access_key, session_token, "us-east-1")
    return cost.get_cost_optimization_recommendations(session, region_name, "EbsVolume")


# ============================================================================
# APPLICATION PERFORMANCE TOOLS
# ============================================================================

@mcp.tool()
def find_target_groups_with_high_error_rate(
    region_name: str = "us-east-1",
    period: int = 7,
    error_threshold: float = 5.0,
    profile_name: str | None = None,
    role_arn: str | None = None,
    access_key: str | None = None,
    secret_access_key: str | None = None,
    session_token: str | None = None,
) -> dict[str, Any]:
    """Find target groups with high error rates (5XX errors).
    
    Args:
        region_name: AWS region name
        period: Lookback period in days (default: 7)
        error_threshold: Error rate threshold percentage (default: 5.0)
        profile_name: AWS profile name (optional)
        role_arn: IAM role ARN to assume (optional)
        access_key: AWS access key ID (optional)
        secret_access_key: AWS secret access key (optional)
        session_token: AWS session token for temporary credentials (optional)
    
    Returns:
        Dictionary with target groups having high error rates
    """
    session = create_session(profile_name, role_arn, access_key, secret_access_key, session_token, region_name)
    return application.find_target_groups_with_high_error_rate(session, region_name, period, error_threshold)


@mcp.tool()
def find_target_groups_with_high_response_time(
    region_name: str = "us-east-1",
    period: int = 7,
    response_time_threshold: float = 1.0,
    profile_name: str | None = None,
    role_arn: str | None = None,
    access_key: str | None = None,
    secret_access_key: str | None = None,
    session_token: str | None = None,
) -> dict[str, Any]:
    """Find target groups with high response times.
    
    Args:
        region_name: AWS region name
        period: Lookback period in days (default: 7)
        response_time_threshold: Response time threshold in seconds (default: 1.0)
        profile_name: AWS profile name (optional)
        role_arn: IAM role ARN to assume (optional)
        access_key: AWS access key ID (optional)
        secret_access_key: AWS secret access key (optional)
        session_token: AWS session token for temporary credentials (optional)
    
    Returns:
        Dictionary with target groups having high response times
    """
    session = create_session(profile_name, role_arn, access_key, secret_access_key, session_token, region_name)
    return application.find_target_groups_with_high_response_time(session, region_name, period, response_time_threshold)


# ============================================================================
# UPGRADE TOOLS
# ============================================================================

# ============================================================================
# COST EXPLORER TOOLS
# ============================================================================

@mcp.tool()
def get_cost_by_region(
    start_date: str | None = None,
    end_date: str | None = None,
    profile_name: str | None = None,
    role_arn: str | None = None,
    access_key: str | None = None,
    secret_access_key: str | None = None,
    session_token: str | None = None,
) -> dict[str, Any]:
    """Get cost breakdown by AWS region for the specified period.
    
    Args:
        start_date: Start date in YYYY-MM-DD format (default: first day of last month)
        end_date: End date in YYYY-MM-DD format (default: first day of current month)
        profile_name: AWS profile name (optional)
        role_arn: IAM role ARN to assume (optional)
        access_key: AWS access key ID (optional)
        secret_access_key: AWS secret access key (optional)
        session_token: AWS session token for temporary credentials (optional)
    
    Returns:
        Dictionary with cost breakdown by region
    """
    session = create_session(profile_name, role_arn, access_key, secret_access_key, session_token, "us-east-1")
    return cost_explorer.get_cost_by_region(session, "us-east-1", start_date, end_date)


@mcp.tool()
def get_cost_by_service(
    start_date: str | None = None,
    end_date: str | None = None,
    profile_name: str | None = None,
    role_arn: str | None = None,
    access_key: str | None = None,
    secret_access_key: str | None = None,
    session_token: str | None = None,
) -> dict[str, Any]:
    """Get cost breakdown by AWS service for the specified period.
    
    Args:
        start_date: Start date in YYYY-MM-DD format (default: first day of last month)
        end_date: End date in YYYY-MM-DD format (default: first day of current month)
        profile_name: AWS profile name (optional)
        role_arn: IAM role ARN to assume (optional)
        access_key: AWS access key ID (optional)
        secret_access_key: AWS secret access key (optional)
        session_token: AWS session token for temporary credentials (optional)
    
    Returns:
        Dictionary with cost breakdown by service
    """
    session = create_session(profile_name, role_arn, access_key, secret_access_key, session_token, "us-east-1")
    return cost_explorer.get_cost_by_service(session, "us-east-1", start_date, end_date)


@mcp.tool()
def get_cost_by_region_and_service(
    start_date: str | None = None,
    end_date: str | None = None,
    profile_name: str | None = None,
    role_arn: str | None = None,
    access_key: str | None = None,
    secret_access_key: str | None = None,
    session_token: str | None = None,
) -> dict[str, Any]:
    """Get cost breakdown by AWS region and service for the specified period.
    
    Args:
        start_date: Start date in YYYY-MM-DD format (default: first day of last month)
        end_date: End date in YYYY-MM-DD format (default: first day of current month)
        profile_name: AWS profile name (optional)
        role_arn: IAM role ARN to assume (optional)
        access_key: AWS access key ID (optional)
        secret_access_key: AWS secret access key (optional)
        session_token: AWS session token for temporary credentials (optional)
    
    Returns:
        Dictionary with cost breakdown by region and service
    """
    session = create_session(profile_name, role_arn, access_key, secret_access_key, session_token, "us-east-1")
    return cost_explorer.get_cost_by_region_and_service(session, "us-east-1", start_date, end_date)


@mcp.tool()
def get_daily_cost_trend(
    days: int = 30,
    profile_name: str | None = None,
    role_arn: str | None = None,
    access_key: str | None = None,
    secret_access_key: str | None = None,
    session_token: str | None = None,
) -> dict[str, Any]:
    """Get daily cost trend for the specified number of days.
    
    Args:
        days: Number of days to look back (default: 30)
        profile_name: AWS profile name (optional)
        role_arn: IAM role ARN to assume (optional)
        access_key: AWS access key ID (optional)
        secret_access_key: AWS secret access key (optional)
        session_token: AWS session token for temporary credentials (optional)
    
    Returns:
        Dictionary with daily cost trend and statistics
    """
    session = create_session(profile_name, role_arn, access_key, secret_access_key, session_token, "us-east-1")
    return cost_explorer.get_daily_cost_trend(session, "us-east-1", days)


# ============================================================================
# UPGRADE TOOLS
# ============================================================================

@mcp.tool()
def find_asgs_with_old_amis(
    region_name: str = "us-east-1",
    period: int = 90,
    max_results: int = 100,
    profile_name: str | None = None,
    role_arn: str | None = None,
    access_key: str | None = None,
    secret_access_key: str | None = None,
    session_token: str | None = None,
) -> dict[str, Any]:
    """Find Auto Scaling Groups using AMIs older than the specified period.
    
    Args:
        region_name: AWS region name
        period: Minimum age in days for AMI to be considered old (default: 90)
        max_results: Maximum results to return (default: 100)
        profile_name: AWS profile name (optional)
        role_arn: IAM role ARN to assume (optional)
        access_key: AWS access key ID (optional)
        secret_access_key: AWS secret access key (optional)
        session_token: AWS session token for temporary credentials (optional)
    
    Returns:
        Dictionary with ASGs using old AMIs
    """
    session = create_session(profile_name, role_arn, access_key, secret_access_key, session_token, region_name)
    return upgrade.find_asgs_with_old_amis(session, region_name, period, max_results)


# ============================================================================
# NETWORK TOOLS
# ============================================================================

@mcp.tool()
def find_unused_nat_gateways(
    region_name: str = "us-east-1",
    period: int = 32,
    max_results: int = 100,
    profile_name: str | None = None,
    role_arn: str | None = None,
    access_key: str | None = None,
    secret_access_key: str | None = None,
    session_token: str | None = None,
) -> dict[str, Any]:
    """Find NAT Gateways with no traffic in the specified period."""
    session = create_session(profile_name, role_arn, access_key, secret_access_key, session_token, region_name)
    return network.find_unused_nat_gateways(session, region_name, period, max_results)


@mcp.tool()
def find_unused_vpc_endpoints(
    region_name: str = "us-east-1",
    period: int = 90,
    max_results: int = 100,
    profile_name: str | None = None,
    role_arn: str | None = None,
    access_key: str | None = None,
    secret_access_key: str | None = None,
    session_token: str | None = None,
) -> dict[str, Any]:
    """Find VPC Endpoints with no connections in the specified period."""
    session = create_session(profile_name, role_arn, access_key, secret_access_key, session_token, region_name)
    return network.find_unused_vpc_endpoints(session, region_name, period, max_results)


@mcp.tool()
def find_unused_internet_gateways(
    region_name: str = "us-east-1",
    max_results: int = 100,
    profile_name: str | None = None,
    role_arn: str | None = None,
    access_key: str | None = None,
    secret_access_key: str | None = None,
    session_token: str | None = None,
) -> dict[str, Any]:
    """Find Internet Gateways not attached or attached to VPCs with no resources."""
    session = create_session(profile_name, role_arn, access_key, secret_access_key, session_token, region_name)
    return network.find_unused_internet_gateways(session, region_name, max_results)


@mcp.tool()
def find_unused_cloudfront_distributions(
    region_name: str = "us-east-1",
    period: int = 90,
    profile_name: str | None = None,
    role_arn: str | None = None,
    access_key: str | None = None,
    secret_access_key: str | None = None,
    session_token: str | None = None,
) -> dict[str, Any]:
    """Find CloudFront distributions with no requests in the specified period."""
    session = create_session(profile_name, role_arn, access_key, secret_access_key, session_token, region_name)
    return network.find_unused_cloudfront_distributions(session, region_name, period)


@mcp.tool()
def find_unused_route53_hosted_zones(
    region_name: str = "us-east-1",
    period: int = 90,
    profile_name: str | None = None,
    role_arn: str | None = None,
    access_key: str | None = None,
    secret_access_key: str | None = None,
    session_token: str | None = None,
) -> dict[str, Any]:
    """Find Route53 hosted zones with no query activity."""
    session = create_session(profile_name, role_arn, access_key, secret_access_key, session_token, region_name)
    return network.find_unused_route53_hosted_zones(session, region_name, period)


# ============================================================================
# STORAGE TOOLS
# ============================================================================

@mcp.tool()
def find_unused_s3_buckets(
    region_name: str = "us-east-1",
    period: int = 90,
    profile_name: str | None = None,
    role_arn: str | None = None,
    access_key: str | None = None,
    secret_access_key: str | None = None,
    session_token: str | None = None,
) -> dict[str, Any]:
    """Find S3 buckets with no activity in the specified period."""
    session = create_session(profile_name, role_arn, access_key, secret_access_key, session_token, region_name)
    return storage.find_unused_s3_buckets(session, region_name, period)


@mcp.tool()
def get_s3_storage_class_recommendations(
    region_name: str = "us-east-1",
    profile_name: str | None = None,
    role_arn: str | None = None,
    access_key: str | None = None,
    secret_access_key: str | None = None,
    session_token: str | None = None,
) -> dict[str, Any]:
    """Get S3 storage class optimization recommendations."""
    session = create_session(profile_name, role_arn, access_key, secret_access_key, session_token, region_name)
    return storage.get_s3_storage_class_recommendations(session, region_name)


# ============================================================================
# CONTAINER TOOLS
# ============================================================================

@mcp.tool()
def find_old_ecs_task_definitions(
    region_name: str = "us-east-1",
    age_days: int = 90,
    profile_name: str | None = None,
    role_arn: str | None = None,
    access_key: str | None = None,
    secret_access_key: str | None = None,
    session_token: str | None = None,
) -> dict[str, Any]:
    """Find old ECS task definitions not used by any service."""
    session = create_session(profile_name, role_arn, access_key, secret_access_key, session_token, region_name)
    return containers.find_old_ecs_task_definitions(session, region_name, age_days)


@mcp.tool()
def find_unused_ecr_images(
    region_name: str = "us-east-1",
    age_days: int = 90,
    profile_name: str | None = None,
    role_arn: str | None = None,
    access_key: str | None = None,
    secret_access_key: str | None = None,
    session_token: str | None = None,
) -> dict[str, Any]:
    """Find unused ECR images older than specified days."""
    session = create_session(profile_name, role_arn, access_key, secret_access_key, session_token, region_name)
    return containers.find_unused_ecr_images(session, region_name, age_days)


@mcp.tool()
def find_unused_launch_templates(
    region_name: str = "us-east-1",
    profile_name: str | None = None,
    role_arn: str | None = None,
    access_key: str | None = None,
    secret_access_key: str | None = None,
    session_token: str | None = None,
) -> dict[str, Any]:
    """Find EC2 launch templates not used by any Auto Scaling Group or instance."""
    session = create_session(profile_name, role_arn, access_key, secret_access_key, session_token, region_name)
    return containers.find_unused_launch_templates(session, region_name)


@mcp.tool()
def find_unused_ecs_clusters_and_services(
    region_name: str = "us-east-1",
    period: int = 90,
    profile_name: str | None = None,
    role_arn: str | None = None,
    access_key: str | None = None,
    secret_access_key: str | None = None,
    session_token: str | None = None,
) -> dict[str, Any]:
    """Find ECS clusters and services with no activity in the specified period.
    
    Identifies:
    - Clusters with no active services, tasks, or scheduled tasks
    - Services with zero running tasks and no recent CloudWatch activity
    """
    session = create_session(profile_name, role_arn, access_key, secret_access_key, session_token, region_name)
    return containers.find_unused_ecs_clusters_and_services(session, region_name, period)


# ============================================================================
# MESSAGING TOOLS
# ============================================================================

@mcp.tool()
def find_unused_sqs_queues(
    region_name: str = "us-east-1",
    period: int = 90,
    profile_name: str | None = None,
    role_arn: str | None = None,
    access_key: str | None = None,
    secret_access_key: str | None = None,
    session_token: str | None = None,
) -> dict[str, Any]:
    """Find SQS queues with no messages sent or received."""
    session = create_session(profile_name, role_arn, access_key, secret_access_key, session_token, region_name)
    return messaging.find_unused_sqs_queues(session, region_name, period)


@mcp.tool()
def find_unused_sns_topics(
    region_name: str = "us-east-1",
    period: int = 90,
    profile_name: str | None = None,
    role_arn: str | None = None,
    access_key: str | None = None,
    secret_access_key: str | None = None,
    session_token: str | None = None,
) -> dict[str, Any]:
    """Find SNS topics with no subscriptions or no messages published."""
    session = create_session(profile_name, role_arn, access_key, secret_access_key, session_token, region_name)
    return messaging.find_unused_sns_topics(session, region_name, period)


@mcp.tool()
def find_unused_eventbridge_rules(
    region_name: str = "us-east-1",
    period: int = 90,
    profile_name: str | None = None,
    role_arn: str | None = None,
    access_key: str | None = None,
    secret_access_key: str | None = None,
    session_token: str | None = None,
) -> dict[str, Any]:
    """Find EventBridge rules with no invocations."""
    session = create_session(profile_name, role_arn, access_key, secret_access_key, session_token, region_name)
    return messaging.find_unused_eventbridge_rules(session, region_name, period)


# ============================================================================
# DATABASE TOOLS
# ============================================================================

@mcp.tool()
def find_unused_dynamodb_tables(
    region_name: str = "us-east-1",
    period: int = 90,
    profile_name: str | None = None,
    role_arn: str | None = None,
    access_key: str | None = None,
    secret_access_key: str | None = None,
    session_token: str | None = None,
) -> dict[str, Any]:
    """Find DynamoDB tables with no read/write activity."""
    session = create_session(profile_name, role_arn, access_key, secret_access_key, session_token, region_name)
    return database.find_unused_dynamodb_tables(session, region_name, period)


@mcp.tool()
def find_underutilized_dynamodb_tables(
    region_name: str = "us-east-1",
    period: int = 30,
    profile_name: str | None = None,
    role_arn: str | None = None,
    access_key: str | None = None,
    secret_access_key: str | None = None,
    session_token: str | None = None,
) -> dict[str, Any]:
    """Find DynamoDB tables with low capacity utilization."""
    session = create_session(profile_name, role_arn, access_key, secret_access_key, session_token, region_name)
    return database.find_underutilized_dynamodb_tables(session, region_name, period)


# ============================================================================
# MONITORING TOOLS
# ============================================================================

@mcp.tool()
def find_unused_cloudwatch_alarms(
    region_name: str = "us-east-1",
    period: int = 90,
    profile_name: str | None = None,
    role_arn: str | None = None,
    access_key: str | None = None,
    secret_access_key: str | None = None,
    session_token: str | None = None,
) -> dict[str, Any]:
    """Find CloudWatch alarms in INSUFFICIENT_DATA state for extended period."""
    session = create_session(profile_name, role_arn, access_key, secret_access_key, session_token, region_name)
    return monitoring.find_unused_cloudwatch_alarms(session, region_name, period)


@mcp.tool()
def find_orphaned_cloudwatch_dashboards(
    region_name: str = "us-east-1",
    period: int = 90,
    profile_name: str | None = None,
    role_arn: str | None = None,
    access_key: str | None = None,
    secret_access_key: str | None = None,
    session_token: str | None = None,
) -> dict[str, Any]:
    """Find CloudWatch dashboards with widgets referencing deleted resources."""
    session = create_session(profile_name, role_arn, access_key, secret_access_key, session_token, region_name)
    return monitoring.find_orphaned_cloudwatch_dashboards(session, region_name, period)


@mcp.tool()
def find_orphaned_cloudwatch_alarms(
    region_name: str = "us-east-1",
    max_results: int = 100,
    profile_name: str | None = None,
    role_arn: str | None = None,
    access_key: str | None = None,
    secret_access_key: str | None = None,
    session_token: str | None = None,
) -> dict[str, Any]:
    """Find CloudWatch alarms not associated with any active AWS resources.
    
    This validates alarms against actual resources across multiple services:
    EC2, RDS, ECS, Lambda, SQS, Target Groups, and Load Balancers.
    """
    session = create_session(profile_name, role_arn, access_key, secret_access_key, session_token, region_name)
    return monitoring.find_orphaned_cloudwatch_alarms(session, region_name, max_results)


# ============================================================================
# CAPACITY DATABASE TOOLS
# ============================================================================

@mcp.tool()
def find_overutilized_dynamodb_tables(
    region_name: str = "us-east-1",
    period: int = 30,
    profile_name: str | None = None,
    role_arn: str | None = None,
    access_key: str | None = None,
    secret_access_key: str | None = None,
    session_token: str | None = None,
) -> dict[str, Any]:
    """Find DynamoDB tables with high capacity utilization (>80%)."""
    session = create_session(profile_name, role_arn, access_key, secret_access_key, session_token, region_name)
    return capacity_database.find_overutilized_dynamodb_tables(session, region_name, period)


@mcp.tool()
def find_underutilized_elasticache_clusters(
    region_name: str = "us-east-1",
    period: int = 30,
    profile_name: str | None = None,
    role_arn: str | None = None,
    access_key: str | None = None,
    secret_access_key: str | None = None,
    session_token: str | None = None,
) -> dict[str, Any]:
    """Find ElastiCache clusters with low CPU utilization (<20%)."""
    session = create_session(profile_name, role_arn, access_key, secret_access_key, session_token, region_name)
    return capacity_database.find_underutilized_elasticache_clusters(session, region_name, period)


@mcp.tool()
def find_overutilized_elasticache_clusters(
    region_name: str = "us-east-1",
    period: int = 30,
    profile_name: str | None = None,
    role_arn: str | None = None,
    access_key: str | None = None,
    secret_access_key: str | None = None,
    session_token: str | None = None,
) -> dict[str, Any]:
    """Find ElastiCache clusters with high CPU or memory utilization (>80%)."""
    session = create_session(profile_name, role_arn, access_key, secret_access_key, session_token, region_name)
    return capacity_database.find_overutilized_elasticache_clusters(session, region_name, period)


@mcp.tool()
def find_underutilized_ecs_services(
    region_name: str = "us-east-1",
    period: int = 30,
    profile_name: str | None = None,
    role_arn: str | None = None,
    access_key: str | None = None,
    secret_access_key: str | None = None,
    session_token: str | None = None,
) -> dict[str, Any]:
    """Find ECS services with low CPU and memory utilization (<20%)."""
    session = create_session(profile_name, role_arn, access_key, secret_access_key, session_token, region_name)
    return capacity_database.find_underutilized_ecs_services(session, region_name, period)


# ============================================================================
# CAPACITY COMPUTE TOOLS
# ============================================================================

@mcp.tool()
def find_underutilized_lambda_functions(
    region_name: str = "us-east-1",
    period: int = 30,
    profile_name: str | None = None,
    role_arn: str | None = None,
    access_key: str | None = None,
    secret_access_key: str | None = None,
    session_token: str | None = None,
) -> dict[str, Any]:
    """Find Lambda functions with low invocation rates or high error rates."""
    session = create_session(profile_name, role_arn, access_key, secret_access_key, session_token, region_name)
    return capacity_compute.find_underutilized_lambda_functions(session, region_name, period)


# ============================================================================
# COST SAVINGS TOOLS
# ============================================================================

@mcp.tool()
def get_savings_plans_recommendations(
    region_name: str = "us-east-1",
    profile_name: str | None = None,
    role_arn: str | None = None,
    access_key: str | None = None,
    secret_access_key: str | None = None,
    session_token: str | None = None,
) -> dict[str, Any]:
    """Get Savings Plans recommendations from AWS Cost Explorer."""
    session = create_session(profile_name, role_arn, access_key, secret_access_key, session_token, region_name)
    return cost_savings.get_savings_plans_recommendations(session, region_name)


@mcp.tool()
def get_reserved_instance_recommendations(
    region_name: str = "us-east-1",
    service: str = "EC2",
    profile_name: str | None = None,
    role_arn: str | None = None,
    access_key: str | None = None,
    secret_access_key: str | None = None,
    session_token: str | None = None,
) -> dict[str, Any]:
    """Get Reserved Instance purchase recommendations from AWS Cost Explorer."""
    session = create_session(profile_name, role_arn, access_key, secret_access_key, session_token, region_name)
    return cost_savings.get_reserved_instance_recommendations(session, region_name, service)


@mcp.tool()
def analyze_reserved_instance_utilization(
    region_name: str = "us-east-1",
    profile_name: str | None = None,
    role_arn: str | None = None,
    access_key: str | None = None,
    secret_access_key: str | None = None,
    session_token: str | None = None,
) -> dict[str, Any]:
    """Analyze Reserved Instance utilization and coverage."""
    session = create_session(profile_name, role_arn, access_key, secret_access_key, session_token, region_name)
    return cost_savings.analyze_reserved_instance_utilization(session, region_name)


# ============================================================================
# COST STORAGE TOOLS
# ============================================================================

@mcp.tool()
def get_ebs_volume_type_recommendations(
    region_name: str = "us-east-1",
    profile_name: str | None = None,
    role_arn: str | None = None,
    access_key: str | None = None,
    secret_access_key: str | None = None,
    session_token: str | None = None,
) -> dict[str, Any]:
    """Get recommendations for optimizing EBS volume types based on usage patterns."""
    session = create_session(profile_name, role_arn, access_key, secret_access_key, session_token, region_name)
    return cost_storage.get_ebs_volume_type_recommendations(session, region_name)


@mcp.tool()
def get_snapshot_lifecycle_recommendations(
    region_name: str = "us-east-1",
    retention_days: int = 30,
    profile_name: str | None = None,
    role_arn: str | None = None,
    access_key: str | None = None,
    secret_access_key: str | None = None,
    session_token: str | None = None,
) -> dict[str, Any]:
    """Get recommendations for snapshot lifecycle management and cleanup."""
    session = create_session(profile_name, role_arn, access_key, secret_access_key, session_token, region_name)
    return cost_storage.get_snapshot_lifecycle_recommendations(session, region_name, retention_days)


# ============================================================================
# COST NETWORK TOOLS
# ============================================================================

@mcp.tool()
def analyze_data_transfer_costs(
    region_name: str = "us-east-1",
    profile_name: str | None = None,
    role_arn: str | None = None,
    access_key: str | None = None,
    secret_access_key: str | None = None,
    session_token: str | None = None,
) -> dict[str, Any]:
    """Analyze data transfer costs using AWS Cost Explorer."""
    session = create_session(profile_name, role_arn, access_key, secret_access_key, session_token, region_name)
    return cost_network.analyze_data_transfer_costs(session, region_name)


@mcp.tool()
def get_nat_gateway_optimization_recommendations(
    region_name: str = "us-east-1",
    profile_name: str | None = None,
    role_arn: str | None = None,
    access_key: str | None = None,
    secret_access_key: str | None = None,
    session_token: str | None = None,
) -> dict[str, Any]:
    """Get recommendations for optimizing NAT Gateway costs."""
    session = create_session(profile_name, role_arn, access_key, secret_access_key, session_token, region_name)
    return cost_network.get_nat_gateway_optimization_recommendations(session, region_name)


# ============================================================================
# UPGRADE DATABASE TOOLS
# ============================================================================

@mcp.tool()
def find_outdated_rds_engine_versions(
    region_name: str = "us-east-1",
    profile_name: str | None = None,
    role_arn: str | None = None,
    access_key: str | None = None,
    secret_access_key: str | None = None,
    session_token: str | None = None,
) -> dict[str, Any]:
    """Find RDS instances not running the latest engine version."""
    session = create_session(profile_name, role_arn, access_key, secret_access_key, session_token, region_name)
    return upgrade_database.find_outdated_rds_engine_versions(session, region_name)


@mcp.tool()
def find_outdated_elasticache_engine_versions(
    region_name: str = "us-east-1",
    profile_name: str | None = None,
    role_arn: str | None = None,
    access_key: str | None = None,
    secret_access_key: str | None = None,
    session_token: str | None = None,
) -> dict[str, Any]:
    """Find ElastiCache clusters not running the latest engine version."""
    session = create_session(profile_name, role_arn, access_key, secret_access_key, session_token, region_name)
    return upgrade_database.find_outdated_elasticache_engine_versions(session, region_name)


# ============================================================================
# UPGRADE COMPUTE TOOLS
# ============================================================================

@mcp.tool()
def find_outdated_lambda_runtimes(
    region_name: str = "us-east-1",
    profile_name: str | None = None,
    role_arn: str | None = None,
    access_key: str | None = None,
    secret_access_key: str | None = None,
    session_token: str | None = None,
) -> dict[str, Any]:
    """Find Lambda functions with deprecated or outdated runtimes."""
    session = create_session(profile_name, role_arn, access_key, secret_access_key, session_token, region_name)
    return upgrade_compute.find_outdated_lambda_runtimes(session, region_name)


@mcp.tool()
def find_ec2_instances_with_old_generations(
    region_name: str = "us-east-1",
    profile_name: str | None = None,
    role_arn: str | None = None,
    access_key: str | None = None,
    secret_access_key: str | None = None,
    session_token: str | None = None,
) -> dict[str, Any]:
    """Find EC2 instances using previous generation instance types."""
    session = create_session(profile_name, role_arn, access_key, secret_access_key, session_token, region_name)
    return upgrade_compute.find_ec2_instances_with_old_generations(session, region_name)


@mcp.tool()
def find_ebs_volumes_with_old_types(
    region_name: str = "us-east-1",
    profile_name: str | None = None,
    role_arn: str | None = None,
    access_key: str | None = None,
    secret_access_key: str | None = None,
    session_token: str | None = None,
) -> dict[str, Any]:
    """Find EBS volumes using previous generation volume types."""
    session = create_session(profile_name, role_arn, access_key, secret_access_key, session_token, region_name)
    return upgrade_compute.find_ebs_volumes_with_old_types(session, region_name)


@mcp.tool()
def find_outdated_ecs_platform_versions(
    region_name: str = "us-east-1",
    profile_name: str | None = None,
    role_arn: str | None = None,
    access_key: str | None = None,
    secret_access_key: str | None = None,
    session_token: str | None = None,
) -> dict[str, Any]:
    """Find ECS services not using the latest platform version."""
    session = create_session(profile_name, role_arn, access_key, secret_access_key, session_token, region_name)
    return upgrade_compute.find_outdated_ecs_platform_versions(session, region_name)


# ============================================================================
# UPGRADE CONTAINERS TOOLS
# ============================================================================

@mcp.tool()
def find_outdated_eks_cluster_versions(
    region_name: str = "us-east-1",
    profile_name: str | None = None,
    role_arn: str | None = None,
    access_key: str | None = None,
    secret_access_key: str | None = None,
    session_token: str | None = None,
) -> dict[str, Any]:
    """Find EKS clusters not running the latest Kubernetes version."""
    session = create_session(profile_name, role_arn, access_key, secret_access_key, session_token, region_name)
    return upgrade_containers.find_outdated_eks_cluster_versions(session, region_name)


# ============================================================================
# PERFORMANCE TOOLS
# ============================================================================

@mcp.tool()
def analyze_lambda_cold_starts(
    region_name: str = "us-east-1",
    period: int = 7,
    profile_name: str | None = None,
    role_arn: str | None = None,
    access_key: str | None = None,
    secret_access_key: str | None = None,
    session_token: str | None = None,
) -> dict[str, Any]:
    """Analyze Lambda functions for cold start issues."""
    session = create_session(profile_name, role_arn, access_key, secret_access_key, session_token, region_name)
    return performance.analyze_lambda_cold_starts(session, region_name, period)


@mcp.tool()
def analyze_api_gateway_performance(
    region_name: str = "us-east-1",
    period: int = 7,
    profile_name: str | None = None,
    role_arn: str | None = None,
    access_key: str | None = None,
    secret_access_key: str | None = None,
    session_token: str | None = None,
) -> dict[str, Any]:
    """Analyze API Gateway performance metrics."""
    session = create_session(profile_name, role_arn, access_key, secret_access_key, session_token, region_name)
    return performance.analyze_api_gateway_performance(session, region_name, period)


@mcp.tool()
def analyze_dynamodb_throttling(
    region_name: str = "us-east-1",
    period: int = 7,
    profile_name: str | None = None,
    role_arn: str | None = None,
    access_key: str | None = None,
    secret_access_key: str | None = None,
    session_token: str | None = None,
) -> dict[str, Any]:
    """Analyze DynamoDB tables for throttling issues."""
    session = create_session(profile_name, role_arn, access_key, secret_access_key, session_token, region_name)
    return performance.analyze_dynamodb_throttling(session, region_name, period)


@mcp.tool()
def analyze_rds_performance_insights(
    region_name: str = "us-east-1",
    period: int = 7,
    profile_name: str | None = None,
    role_arn: str | None = None,
    access_key: str | None = None,
    secret_access_key: str | None = None,
    session_token: str | None = None,
) -> dict[str, Any]:
    """Analyze RDS Performance Insights data."""
    session = create_session(profile_name, role_arn, access_key, secret_access_key, session_token, region_name)
    return performance.analyze_rds_performance_insights(session, region_name, period)


@mcp.tool()
def analyze_cloudfront_cache_hit_ratio(
    region_name: str = "us-east-1",
    period: int = 7,
    profile_name: str | None = None,
    role_arn: str | None = None,
    access_key: str | None = None,
    secret_access_key: str | None = None,
    session_token: str | None = None,
) -> dict[str, Any]:
    """Analyze CloudFront cache hit ratios."""
    session = create_session(profile_name, role_arn, access_key, secret_access_key, session_token, region_name)
    return performance.analyze_cloudfront_cache_hit_ratio(session, region_name, period)


# ============================================================================
# SECURITY TOOLS
# ============================================================================

@mcp.tool()
def find_unencrypted_ebs_volumes(
    region_name: str = "us-east-1",
    profile_name: str | None = None,
    role_arn: str | None = None,
    access_key: str | None = None,
    secret_access_key: str | None = None,
    session_token: str | None = None,
) -> dict[str, Any]:
    """Find EBS volumes without encryption enabled."""
    session = create_session(profile_name, role_arn, access_key, secret_access_key, session_token, region_name)
    return security.find_unencrypted_ebs_volumes(session, region_name)


@mcp.tool()
def find_unencrypted_s3_buckets(
    region_name: str = "us-east-1",
    profile_name: str | None = None,
    role_arn: str | None = None,
    access_key: str | None = None,
    secret_access_key: str | None = None,
    session_token: str | None = None,
) -> dict[str, Any]:
    """Find S3 buckets without default encryption enabled."""
    session = create_session(profile_name, role_arn, access_key, secret_access_key, session_token, region_name)
    return security.find_unencrypted_s3_buckets(session, region_name)


@mcp.tool()
def find_unencrypted_rds_instances(
    region_name: str = "us-east-1",
    profile_name: str | None = None,
    role_arn: str | None = None,
    access_key: str | None = None,
    secret_access_key: str | None = None,
    session_token: str | None = None,
) -> dict[str, Any]:
    """Find RDS instances without encryption enabled."""
    session = create_session(profile_name, role_arn, access_key, secret_access_key, session_token, region_name)
    return security.find_unencrypted_rds_instances(session, region_name)


@mcp.tool()
def find_public_s3_buckets(
    region_name: str = "us-east-1",
    profile_name: str | None = None,
    role_arn: str | None = None,
    access_key: str | None = None,
    secret_access_key: str | None = None,
    session_token: str | None = None,
) -> dict[str, Any]:
    """Find S3 buckets with public access enabled."""
    session = create_session(profile_name, role_arn, access_key, secret_access_key, session_token, region_name)
    return security.find_public_s3_buckets(session, region_name)


@mcp.tool()
def find_overly_permissive_security_groups(
    region_name: str = "us-east-1",
    profile_name: str | None = None,
    role_arn: str | None = None,
    access_key: str | None = None,
    secret_access_key: str | None = None,
    session_token: str | None = None,
) -> dict[str, Any]:
    """Find security groups with overly permissive rules (0.0.0.0/0 or ::/0)."""
    session = create_session(profile_name, role_arn, access_key, secret_access_key, session_token, region_name)
    return security.find_overly_permissive_security_groups(session, region_name)


# ============================================================================
# GOVERNANCE TOOLS
# ============================================================================

@mcp.tool()
def find_untagged_resources(
    region_name: str = "us-east-1",
    required_tags: list[str] | None = None,
    profile_name: str | None = None,
    role_arn: str | None = None,
    access_key: str | None = None,
    secret_access_key: str | None = None,
    session_token: str | None = None,
) -> dict[str, Any]:
    """Find AWS resources missing required tags."""
    session = create_session(profile_name, role_arn, access_key, secret_access_key, session_token, region_name)
    return governance.find_untagged_resources(session, region_name, required_tags)


@mcp.tool()
def analyze_tag_compliance(
    region_name: str = "us-east-1",
    required_tags: list[str] | None = None,
    profile_name: str | None = None,
    role_arn: str | None = None,
    access_key: str | None = None,
    secret_access_key: str | None = None,
    session_token: str | None = None,
) -> dict[str, Any]:
    """Analyze tag compliance across AWS resources."""
    session = create_session(profile_name, role_arn, access_key, secret_access_key, session_token, region_name)
    return governance.analyze_tag_compliance(session, region_name, required_tags)


@mcp.tool()
def generate_cost_allocation_report(
    region_name: str = "us-east-1",
    profile_name: str | None = None,
    role_arn: str | None = None,
    access_key: str | None = None,
    secret_access_key: str | None = None,
    session_token: str | None = None,
) -> dict[str, Any]:
    """Generate cost allocation report based on resource tags."""
    session = create_session(profile_name, role_arn, access_key, secret_access_key, session_token, region_name)
    return governance.generate_cost_allocation_report(session, region_name)
