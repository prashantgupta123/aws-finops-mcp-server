# Tool Categories Guide

The AWS FinOps MCP Server supports **category-based tool filtering** to reduce the number of exposed tools and improve client performance. Instead of loading all 70+ tools, you can selectively enable only the categories you need.

## Quick Start

Set the `MCP_TOOL_CATEGORIES` environment variable to control which tool categories are enabled:

```bash
# Enable only cleanup and cost tools
export MCP_TOOL_CATEGORIES="cleanup,cost"
python -m aws_finops_mcp

# Enable all tools (default)
export MCP_TOOL_CATEGORIES="all"
python -m aws_finops_mcp

# Or omit the variable entirely for all tools
python -m aws_finops_mcp
```

## Available Categories

### 1. **cleanup** (9 tools)
Find and identify unused AWS resources that can be safely removed.

**Tools:**
- `find_unused_lambda_functions` - Lambda functions with no invocations
- `find_unused_elastic_ips` - Unattached Elastic IPs
- `find_unused_amis` - AMIs not used by instances or ASGs
- `find_unused_load_balancers` - Load balancers with no traffic
- `find_unused_target_groups` - Target groups with no targets or traffic
- `find_unused_log_groups` - CloudWatch Log Groups with no recent events
- `find_unused_snapshots` - EBS snapshots not associated with AMIs/volumes
- `find_unused_security_groups` - Security groups not attached to resources
- `find_unused_volumes` - Unattached EBS volumes

**Use Case:** Regular cleanup audits, cost reduction initiatives

---

### 2. **capacity** (9 tools)
Analyze resource utilization to identify over/under-provisioned resources.

**Tools:**
- `find_underutilized_ec2_instances` - EC2 with low CPU/memory (≤20%)
- `find_overutilized_ec2_instances` - EC2 with high CPU/memory (≥80%)
- `find_underutilized_rds_instances` - RDS with low CPU (≤20%)
- `find_overutilized_rds_instances` - RDS with high CPU (≥80%)
- `find_overutilized_dynamodb_tables` - DynamoDB with high capacity (>80%)
- `find_underutilized_elasticache_clusters` - ElastiCache with low CPU (<20%)
- `find_overutilized_elasticache_clusters` - ElastiCache with high CPU/memory (>80%)
- `find_underutilized_ecs_services` - ECS services with low CPU/memory (<20%)
- `find_underutilized_lambda_functions` - Lambda with low invocations or high errors

**Use Case:** Right-sizing initiatives, performance optimization

---

### 3. **cost** (16 tools)
Cost analysis, optimization recommendations, and savings opportunities.

**Tools:**
- `get_all_cost_optimization_recommendations` - All AWS Cost Optimization Hub recommendations
- `get_cost_optimization_ec2` - EC2-specific cost recommendations
- `get_cost_optimization_lambda` - Lambda cost recommendations
- `get_cost_optimization_rds` - RDS cost recommendations
- `get_cost_optimization_ebs` - EBS cost recommendations
- `get_cost_by_region` - Cost breakdown by AWS region
- `get_cost_by_service` - Cost breakdown by AWS service
- `get_cost_by_region_and_service` - Combined region and service breakdown
- `get_daily_cost_trend` - Daily cost trends and statistics
- `get_savings_plans_recommendations` - Savings Plans recommendations
- `get_reserved_instance_recommendations` - Reserved Instance purchase recommendations
- `analyze_reserved_instance_utilization` - RI utilization and coverage analysis
- `get_ebs_volume_type_recommendations` - EBS volume type optimization
- `get_snapshot_lifecycle_recommendations` - Snapshot lifecycle management
- `analyze_data_transfer_costs` - Data transfer cost analysis
- `get_nat_gateway_optimization_recommendations` - NAT Gateway cost optimization

**Use Case:** Monthly cost reviews, budget planning, savings initiatives

---

### 4. **application** (2 tools)
Application performance and health monitoring.

**Tools:**
- `find_target_groups_with_high_error_rate` - Target groups with 5XX errors
- `find_target_groups_with_high_response_time` - Target groups with slow response times

**Use Case:** Application health monitoring, SLA compliance

---

### 5. **upgrade** (8 tools)
Identify outdated resources that need upgrades or migrations.

**Tools:**
- `find_asgs_with_old_amis` - Auto Scaling Groups using old AMIs
- `find_outdated_rds_engine_versions` - RDS not on latest engine version
- `find_outdated_elasticache_engine_versions` - ElastiCache not on latest version
- `find_outdated_lambda_runtimes` - Lambda with deprecated runtimes
- `find_ec2_instances_with_old_generations` - EC2 using previous generation types
- `find_ebs_volumes_with_old_types` - EBS using previous generation types
- `find_outdated_ecs_platform_versions` - ECS not on latest platform version
- `find_outdated_eks_cluster_versions` - EKS not on latest Kubernetes version

**Use Case:** Modernization projects, security compliance, performance improvements

---

### 6. **network** (5 tools)
Network resource optimization and cleanup.

**Tools:**
- `find_unused_nat_gateways` - NAT Gateways with no traffic
- `find_unused_vpc_endpoints` - VPC Endpoints with no connections
- `find_unused_internet_gateways` - Unattached Internet Gateways
- `find_unused_cloudfront_distributions` - CloudFront with no requests
- `find_unused_route53_hosted_zones` - Route53 zones with no queries

**Use Case:** Network cost optimization, infrastructure cleanup

---

### 7. **storage** (2 tools)
Storage optimization and recommendations.

**Tools:**
- `find_unused_s3_buckets` - S3 buckets with no activity
- `get_s3_storage_class_recommendations` - S3 storage class optimization

**Use Case:** Storage cost optimization, data lifecycle management

---

### 8. **containers** (4 tools)
Container and orchestration resource management.

**Tools:**
- `find_old_ecs_task_definitions` - Old ECS task definitions not in use
- `find_unused_ecr_images` - Unused ECR images
- `find_unused_launch_templates` - EC2 launch templates not in use
- `find_unused_ecs_clusters_and_services` - ECS clusters/services with no activity

**Use Case:** Container cleanup, ECS/EKS optimization

---

### 9. **messaging** (3 tools)
Messaging service optimization.

**Tools:**
- `find_unused_sqs_queues` - SQS queues with no messages
- `find_unused_sns_topics` - SNS topics with no subscriptions/messages
- `find_unused_eventbridge_rules` - EventBridge rules with no invocations

**Use Case:** Messaging infrastructure cleanup

---

### 10. **database** (2 tools)
Database resource analysis.

**Tools:**
- `find_unused_dynamodb_tables` - DynamoDB tables with no read/write activity
- `find_underutilized_dynamodb_tables` - DynamoDB with low capacity utilization

**Use Case:** Database cost optimization

---

### 11. **monitoring** (3 tools)
Monitoring resource cleanup and optimization.

**Tools:**
- `find_unused_cloudwatch_alarms` - CloudWatch alarms in INSUFFICIENT_DATA state
- `find_orphaned_cloudwatch_dashboards` - Dashboards referencing deleted resources
- `find_orphaned_cloudwatch_alarms` - Alarms not associated with active resources

**Use Case:** Monitoring infrastructure cleanup

---

### 12. **performance** (5 tools)
Performance analysis and optimization.

**Tools:**
- `analyze_lambda_cold_starts` - Lambda cold start analysis
- `analyze_api_gateway_performance` - API Gateway performance metrics
- `analyze_dynamodb_throttling` - DynamoDB throttling issues
- `analyze_rds_performance_insights` - RDS Performance Insights data
- `analyze_cloudfront_cache_hit_ratio` - CloudFront cache performance

**Use Case:** Performance tuning, latency optimization

---

### 13. **security** (5 tools)
Security compliance and best practices.

**Tools:**
- `find_unencrypted_ebs_volumes` - EBS volumes without encryption
- `find_unencrypted_s3_buckets` - S3 buckets without default encryption
- `find_unencrypted_rds_instances` - RDS instances without encryption
- `find_public_s3_buckets` - S3 buckets with public access
- `find_overly_permissive_security_groups` - Security groups with 0.0.0.0/0 rules

**Use Case:** Security audits, compliance checks

---

### 14. **governance** (3 tools)
Resource governance and tagging compliance.

**Tools:**
- `find_untagged_resources` - Resources missing required tags
- `analyze_tag_compliance` - Tag compliance analysis across resources
- `generate_cost_allocation_report` - Cost allocation by tags

**Use Case:** Governance enforcement, cost allocation, compliance

---

## Usage Examples

### Example 1: Cost-Focused Analysis
```bash
export MCP_TOOL_CATEGORIES="cost,cleanup"
python -m aws_finops_mcp
```
Enables 25 tools focused on cost optimization and resource cleanup.

### Example 2: Security Audit
```bash
export MCP_TOOL_CATEGORIES="security,governance"
python -m aws_finops_mcp
```
Enables 8 tools for security compliance and governance.

### Example 3: Performance Optimization
```bash
export MCP_TOOL_CATEGORIES="performance,capacity,application"
python -m aws_finops_mcp
```
Enables 16 tools for performance analysis and capacity planning.

### Example 4: Infrastructure Cleanup
```bash
export MCP_TOOL_CATEGORIES="cleanup,network,storage,containers,messaging,monitoring"
python -m aws_finops_mcp
```
Enables 26 tools for comprehensive infrastructure cleanup.

### Example 5: Single Category
```bash
export MCP_TOOL_CATEGORIES="cleanup"
python -m aws_finops_mcp
```
Enables only 9 cleanup tools.

## Configuration in MCP Clients

### Claude Desktop (macOS)
Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "aws-finops": {
      "command": "python",
      "args": ["-m", "aws_finops_mcp"],
      "env": {
        "MCP_TOOL_CATEGORIES": "cleanup,cost,security"
      }
    }
  }
}
```

### Cline / Other MCP Clients
Add to your MCP configuration:

```json
{
  "mcpServers": {
    "aws-finops": {
      "command": "uvx",
      "args": ["aws-finops-mcp"],
      "env": {
        "MCP_TOOL_CATEGORIES": "cost,capacity"
      }
    }
  }
}
```

### Docker
```bash
docker run -e MCP_TOOL_CATEGORIES="cleanup,cost" aws-finops-mcp
```

### Docker Compose
```yaml
services:
  aws-finops-mcp:
    image: aws-finops-mcp
    environment:
      - MCP_TOOL_CATEGORIES=cleanup,cost,security
```

## Benefits

1. **Faster Client Loading**: Reduce tool count from 70+ to only what you need
2. **Improved Performance**: Less memory and processing overhead
3. **Better Organization**: Focus on specific use cases
4. **Easier Navigation**: Clients show only relevant tools
5. **Flexible Configuration**: Change categories without code changes

## Validation

The server validates category names on startup. If you specify an invalid category, you'll see an error:

```
ValueError: Invalid categories: {'invalid'}. 
Valid categories are: application, capacity, cleanup, containers, cost, 
database, governance, messaging, monitoring, network, performance, 
security, storage, upgrade
```

## Default Behavior

If `MCP_TOOL_CATEGORIES` is not set or set to `"all"`, all 70+ tools are enabled (backward compatible).

## Tool Count by Category

| Category | Tool Count |
|----------|------------|
| cleanup | 9 |
| capacity | 9 |
| cost | 16 |
| application | 2 |
| upgrade | 8 |
| network | 5 |
| storage | 2 |
| containers | 4 |
| messaging | 3 |
| database | 2 |
| monitoring | 3 |
| performance | 5 |
| security | 5 |
| governance | 3 |
| **TOTAL** | **76** |
