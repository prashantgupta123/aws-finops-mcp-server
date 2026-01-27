# Quick Reference - All 49 New Tools

## 🚀 Quick Tool Lookup

### Network & Infrastructure (5 tools)
| ID | Tool Name | Purpose |
|----|-----------|---------|
| 201 | find_unused_nat_gateways | Find NAT Gateways with no traffic |
| 202 | find_unused_vpc_endpoints | Find VPC Endpoints with no connections |
| 203 | find_unused_internet_gateways | Find Internet Gateways not in use |
| 205 | find_unused_cloudfront_distributions | Find CloudFront distributions with no requests |
| 206 | find_unused_route53_hosted_zones | Find Route53 zones with no queries |

### Storage (2 tools)
| ID | Tool Name | Purpose |
|----|-----------|---------|
| 204 | find_unused_s3_buckets | Find S3 buckets with no activity |
| 301 | get_s3_storage_class_recommendations | Get S3 storage class optimization recommendations |

### Containers (3 tools)
| ID | Tool Name | Purpose |
|----|-----------|---------|
| 207 | find_old_ecs_task_definitions | Find old ECS task definitions |
| 208 | find_unused_ecr_images | Find unused ECR images |
| 209 | find_unused_launch_templates | Find unused EC2 launch templates |

### Messaging (3 tools)
| ID | Tool Name | Purpose |
|----|-----------|---------|
| 210 | find_unused_sqs_queues | Find SQS queues with no messages |
| 211 | find_unused_sns_topics | Find SNS topics with no subscriptions |
| 212 | find_unused_eventbridge_rules | Find EventBridge rules with no invocations |

### Database (2 tools)
| ID | Tool Name | Purpose |
|----|-----------|---------|
| 213 | find_unused_dynamodb_tables | Find DynamoDB tables with no activity |
| 214 | find_underutilized_dynamodb_tables | Find DynamoDB tables with low utilization |

### Monitoring (2 tools)
| ID | Tool Name | Purpose |
|----|-----------|---------|
| 215 | find_unused_cloudwatch_alarms | Find CloudWatch alarms in INSUFFICIENT_DATA state |
| 216 | find_orphaned_cloudwatch_dashboards | Find CloudWatch dashboards with deleted resources |

### Capacity Analysis (5 tools)
| ID | Tool Name | Purpose |
|----|-----------|---------|
| 217 | find_overutilized_dynamodb_tables | Find DynamoDB tables with high utilization (>80%) |
| 218 | find_underutilized_elasticache_clusters | Find ElastiCache clusters with low CPU (<20%) |
| 219 | find_overutilized_elasticache_clusters | Find ElastiCache clusters with high utilization (>80%) |
| 220 | find_underutilized_ecs_services | Find ECS services with low utilization |
| 221 | find_underutilized_lambda_functions | Find Lambda functions with low invocations |

### Cost Savings (3 tools) ⭐ HIGH PRIORITY
| ID | Tool Name | Purpose |
|----|-----------|---------|
| 302 | get_savings_plans_recommendations | Get Savings Plans purchase recommendations |
| 303 | get_reserved_instance_recommendations | Get Reserved Instance purchase recommendations |
| 304 | analyze_reserved_instance_utilization | Analyze RI utilization and identify waste |

### Cost Optimization (4 tools)
| ID | Tool Name | Purpose |
|----|-----------|---------|
| 305 | get_ebs_volume_type_recommendations | Get EBS volume type optimization recommendations |
| 306 | get_snapshot_lifecycle_recommendations | Get snapshot cleanup recommendations |
| 307 | analyze_data_transfer_costs | Analyze data transfer costs |
| 308 | get_nat_gateway_optimization_recommendations | Get NAT Gateway cost optimization recommendations |

### Upgrade Recommendations (7 tools) ⭐ HIGH PRIORITY
| ID | Tool Name | Purpose |
|----|-----------|---------|
| 401 | find_outdated_rds_engine_versions | Find RDS instances not on latest engine version |
| 402 | find_outdated_elasticache_engine_versions | Find ElastiCache clusters not on latest version |
| 403 | find_outdated_lambda_runtimes | Find Lambda functions with deprecated runtimes |
| 404 | find_ec2_instances_with_old_generations | Find EC2 instances using old generation types |
| 405 | find_ebs_volumes_with_old_types | Find EBS volumes using old types (gp2, io1) |
| 406 | find_outdated_ecs_platform_versions | Find ECS services not on latest platform version |
| 407 | find_outdated_eks_cluster_versions | Find EKS clusters not on latest Kubernetes version |

### Performance Analysis (5 tools)
| ID | Tool Name | Purpose |
|----|-----------|---------|
| 501 | analyze_lambda_cold_starts | Analyze Lambda functions for cold start issues |
| 502 | analyze_api_gateway_performance | Analyze API Gateway latency and errors |
| 503 | analyze_dynamodb_throttling | Analyze DynamoDB tables for throttling |
| 504 | analyze_rds_performance_insights | Analyze RDS performance metrics |
| 505 | analyze_cloudfront_cache_hit_ratio | Analyze CloudFront cache hit ratios |

### Security & Compliance (5 tools) ⭐ HIGH PRIORITY
| ID | Tool Name | Purpose |
|----|-----------|---------|
| 601 | find_unencrypted_ebs_volumes | Find EBS volumes without encryption |
| 602 | find_unencrypted_s3_buckets | Find S3 buckets without default encryption |
| 603 | find_unencrypted_rds_instances | Find RDS instances without encryption |
| 604 | find_public_s3_buckets | Find S3 buckets with public access |
| 605 | find_overly_permissive_security_groups | Find security groups with 0.0.0.0/0 rules |

### Governance & Tagging (3 tools)
| ID | Tool Name | Purpose |
|----|-----------|---------|
| 701 | find_untagged_resources | Find resources missing required tags |
| 702 | analyze_tag_compliance | Analyze tag compliance across services |
| 703 | generate_cost_allocation_report | Generate cost allocation report by tags |

---

## 📁 Module Files

| Module | Tools | File Path |
|--------|-------|-----------|
| network | 5 | `src/aws_finops_mcp/tools/network.py` |
| storage | 2 | `src/aws_finops_mcp/tools/storage.py` |
| containers | 3 | `src/aws_finops_mcp/tools/containers.py` |
| messaging | 3 | `src/aws_finops_mcp/tools/messaging.py` |
| database | 2 | `src/aws_finops_mcp/tools/database.py` |
| monitoring | 2 | `src/aws_finops_mcp/tools/monitoring.py` |
| capacity_database | 4 | `src/aws_finops_mcp/tools/capacity_database.py` |
| capacity_compute | 1 | `src/aws_finops_mcp/tools/capacity_compute.py` |
| cost_savings | 3 | `src/aws_finops_mcp/tools/cost_savings.py` |
| cost_storage | 2 | `src/aws_finops_mcp/tools/cost_storage.py` |
| cost_network | 2 | `src/aws_finops_mcp/tools/cost_network.py` |
| upgrade_database | 2 | `src/aws_finops_mcp/tools/upgrade_database.py` |
| upgrade_compute | 4 | `src/aws_finops_mcp/tools/upgrade_compute.py` |
| upgrade_containers | 1 | `src/aws_finops_mcp/tools/upgrade_containers.py` |
| performance | 5 | `src/aws_finops_mcp/tools/performance.py` |
| security | 5 | `src/aws_finops_mcp/tools/security.py` |
| governance | 3 | `src/aws_finops_mcp/tools/governance.py` |

---

## 🎯 Usage Examples

### Cost Savings
```python
# Get Savings Plans recommendations
result = get_savings_plans_recommendations(session, region_name="us-east-1")
print(f"Potential monthly savings: {result['total_monthly_savings']}")

# Get Reserved Instance recommendations
result = get_reserved_instance_recommendations(session, service="EC2")
print(f"Found {result['count']} RI recommendations")
```

### Security
```python
# Find unencrypted EBS volumes
result = find_unencrypted_ebs_volumes(session, region_name="us-east-1")
print(f"Found {result['count']} unencrypted volumes")

# Find public S3 buckets
result = find_public_s3_buckets(session)
print(f"Found {result['count']} public buckets")
```

### Upgrade Recommendations
```python
# Find outdated Lambda runtimes
result = find_outdated_lambda_runtimes(session, region_name="us-east-1")
print(f"Found {result['count']} functions with deprecated runtimes")

# Find outdated RDS engines
result = find_outdated_rds_engine_versions(session, region_name="us-east-1")
print(f"Found {result['count']} RDS instances needing upgrades")
```

### Performance
```python
# Analyze Lambda cold starts
result = analyze_lambda_cold_starts(session, region_name="us-east-1", period=7)
print(f"Found {result['count']} functions with cold start issues")

# Analyze API Gateway performance
result = analyze_api_gateway_performance(session, region_name="us-east-1")
print(f"Found {result['count']} APIs with performance issues")
```

---

## 💡 Common Parameters

Most tools accept these parameters:
- `session`: Boto3 session (required)
- `region_name`: AWS region (default: "us-east-1")
- `period`: Lookback period in days (default: 30-90)
- `max_results`: Maximum results to return (default: 100)

Cost Explorer tools always use `region_name="us-east-1"` as it's a global service.

---

## 📊 Response Format

All tools return a standardized dictionary:
```python
{
    "id": 302,  # Unique tool ID
    "name": "Tool Display Name",
    "fields": {  # Field definitions
        "1": "FieldName1",
        "2": "FieldName2",
        ...
    },
    "headers": [...],  # Column headers
    "count": 10,  # Number of resources found
    "total_monthly_cost": "$1,234.56",  # Optional: total cost
    "resource": [  # List of resources
        {
            "FieldName1": "value1",
            "FieldName2": "value2",
            ...
        }
    ]
}
```

---

## 🔍 Finding Tools by Use Case

### "I want to reduce costs"
- 302: Savings Plans recommendations
- 303: Reserved Instance recommendations
- 304: RI utilization analysis
- 305: EBS volume type optimization
- 306: Snapshot lifecycle management
- 307: Data transfer cost analysis
- 308: NAT Gateway optimization
- All "find_unused_*" tools (201-216)

### "I want to improve security"
- 601: Unencrypted EBS volumes
- 602: Unencrypted S3 buckets
- 603: Unencrypted RDS instances
- 604: Public S3 buckets
- 605: Overly permissive security groups

### "I want to upgrade resources"
- 401: Outdated RDS engines
- 402: Outdated ElastiCache engines
- 403: Outdated Lambda runtimes
- 404: Old generation EC2 instances
- 405: Old EBS volume types
- 406: Outdated ECS platform versions
- 407: Outdated EKS versions

### "I want to improve performance"
- 501: Lambda cold starts
- 502: API Gateway performance
- 503: DynamoDB throttling
- 504: RDS performance
- 505: CloudFront cache hit ratio

### "I want better governance"
- 701: Untagged resources
- 702: Tag compliance analysis
- 703: Cost allocation report

---

## ⚡ Quick Start

1. **Import the tool**:
```python
from src.aws_finops_mcp.tools.cost_savings import get_savings_plans_recommendations
```

2. **Create a session**:
```python
import boto3
session = boto3.Session(profile_name="your-profile")
```

3. **Run the tool**:
```python
result = get_savings_plans_recommendations(session)
print(f"Found {result['count']} recommendations")
print(f"Potential savings: {result['total_monthly_savings']}")
```

---

## 📚 Documentation Files

- **IMPLEMENTATION_STATUS.md** - Complete implementation status
- **COMPLETION_SUMMARY.md** - Executive summary
- **QUICK_REFERENCE.md** - This file
- **MISSING_TOOLS_ANALYSIS.md** - Original analysis
- **IMPLEMENTATION_PLAN.md** - Implementation guide
- **COMPLETE_IMPLEMENTATION_GUIDE.md** - Detailed guide

---

**Total Tools**: 74 (25 existing + 49 new)
**Status**: ✅ All implemented and validated
**Next Step**: Integration into MCP server
