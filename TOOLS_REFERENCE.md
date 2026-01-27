# AWS FinOps MCP Server - Tools Reference

Complete reference for all 23 tools available in the AWS FinOps MCP Server.

## Table of Contents

- [Cleanup Tools (9)](#cleanup-tools)
- [Capacity Tools (4)](#capacity-tools)
- [Cost Optimization Tools (5)](#cost-optimization-tools)
- [Application Performance Tools (2)](#application-performance-tools)
- [Upgrade Tools (1)](#upgrade-tools)

---

## Cleanup Tools

### 1. find_unused_lambda_functions

**Purpose**: Identify Lambda functions with no invocations in the specified period.

**Parameters**:
- `region_name` (str, default: "us-east-1"): AWS region
- `period` (int, default: 90): Lookback period in days
- `max_results` (int, default: 100): Maximum results to return
- Plus authentication parameters

**Returns**:
```json
{
  "id": 101,
  "name": "Unused Lambda Functions",
  "count": 5,
  "resource": [
    {
      "FunctionName": "old-function",
      "Runtime": "python3.8",
      "MemorySize": 128,
      "LastModified": "2023-01-15T10:30:00.000+0000",
      "Description": "Lambda function not invoked in the last 90 days"
    }
  ]
}
```

**Use Case**: Identify Lambda functions that can be safely deleted to reduce costs.

---

### 2. find_unused_elastic_ips

**Purpose**: Find Elastic IPs not attached to any instance.

**Parameters**:
- `region_name` (str, default: "us-east-1"): AWS region
- Plus authentication parameters

**Returns**:
```json
{
  "id": 106,
  "name": "Unused Elastic IPs",
  "count": 3,
  "resource": [
    {
      "PublicIp": "54.123.45.67",
      "AllocationId": "eipalloc-12345678",
      "Name": "old-eip",
      "Domain": "vpc",
      "Description": "Unused Elastic IP - not attached to any instance"
    }
  ]
}
```

**Use Case**: Unattached EIPs incur charges. Release them to save costs.

---

### 3. find_unused_amis

**Purpose**: Find AMIs not used by any EC2 instances, ASGs, or Spot Fleet Requests.

**Parameters**:
- `region_name` (str, default: "us-east-1"): AWS region
- `period` (int, default: 90): Minimum age in days
- `max_results` (int, default: 100): Maximum results
- Plus authentication parameters

**Returns**:
```json
{
  "id": 107,
  "name": "Unused AMIs",
  "count": 10,
  "resource": [
    {
      "ImageId": "ami-12345678",
      "Name": "old-app-image",
      "CreationDate": "2023-01-01T00:00:00.000Z",
      "Age": "365 days",
      "Platform": "Linux/UNIX",
      "Description": "AMI not used by any EC2 instances or Auto Scaling Groups"
    }
  ]
}
```

**Use Case**: Old AMIs and their snapshots consume storage. Clean up to reduce costs.

---

### 4. find_unused_load_balancers

**Purpose**: Find load balancers with no traffic in the specified period.

**Parameters**:
- `region_name` (str, default: "us-east-1"): AWS region
- `period` (int, default: 90): Lookback period in days
- Plus authentication parameters

**Returns**:
```json
{
  "id": 103,
  "name": "Unused Load Balancers",
  "count": 2,
  "resource": [
    {
      "Name": "app/old-alb/abc123",
      "Type": "ALB",
      "DNSName": "old-alb-123.us-east-1.elb.amazonaws.com",
      "Scheme": "internet-facing",
      "VpcId": "vpc-12345678",
      "Description": "Load Balancer with no traffic in the last 90 days"
    }
  ]
}
```

**Use Case**: Unused load balancers cost ~$16-25/month. Delete to save costs.

---

### 5. find_unused_target_groups

**Purpose**: Find target groups with no registered targets.

**Parameters**:
- `region_name` (str, default: "us-east-1"): AWS region
- `max_results` (int, default: 100): Maximum results
- Plus authentication parameters

**Returns**:
```json
{
  "id": 104,
  "name": "Unused Target Groups",
  "count": 5,
  "resource": [
    {
      "TargetGroupName": "old-tg",
      "Protocol": "HTTP",
      "Port": 80,
      "VpcId": "vpc-12345678",
      "LoadBalancerCount": 0,
      "Description": "Target group with no registered targets"
    }
  ]
}
```

**Use Case**: Clean up orphaned target groups for better organization.

---

### 6. find_unused_log_groups

**Purpose**: Find CloudWatch Log Groups with no recent log events.

**Parameters**:
- `region_name` (str, default: "us-east-1"): AWS region
- `period` (int, default: 90): Lookback period in days
- `max_results` (int, default: 50): Maximum results
- Plus authentication parameters

**Returns**:
```json
{
  "id": 105,
  "name": "Unused Log Groups",
  "count": 15,
  "resource": [
    {
      "LogGroupName": "/aws/lambda/old-function",
      "LastEventTime": "2023-01-01T00:00:00",
      "StoredMB": "1024.50",
      "RetentionDays": "Never Expire",
      "Description": "Log group with no events in the last 90 days"
    }
  ]
}
```

**Use Case**: Log storage costs $0.03/GB/month. Delete old logs to save costs.

---

### 7. find_unused_snapshots

**Purpose**: Find EBS snapshots not associated with any AMI or volume.

**Parameters**:
- `region_name` (str, default: "us-east-1"): AWS region
- `period` (int, default: 90): Minimum age in days
- `max_results` (int, default: 100): Maximum results
- Plus authentication parameters

**Returns**:
```json
{
  "id": 108,
  "name": "Unused Snapshots",
  "count": 20,
  "resource": [
    {
      "SnapshotId": "snap-12345678",
      "Description": "Manual snapshot",
      "StartTime": "2023-01-01T00:00:00",
      "Age": "365 days",
      "SizeGB": 100,
      "State": "completed"
    }
  ]
}
```

**Use Case**: Snapshots cost $0.05/GB/month. Delete unused ones to save costs.

---

### 8. find_unused_security_groups

**Purpose**: Find security groups not attached to any resources.

**Parameters**:
- `region_name` (str, default: "us-east-1"): AWS region
- `max_results` (int, default: 100): Maximum results
- Plus authentication parameters

**Returns**:
```json
{
  "id": 114,
  "name": "Unused Security Groups",
  "count": 10,
  "resource": [
    {
      "SecurityGroupID": "sg-12345678",
      "SecurityGroupName": "old-sg",
      "Description": "Old security group",
      "VpcId": "vpc-12345678",
      "InboundRulesCount": 3,
      "OutboundRulesCount": 1
    }
  ]
}
```

**Use Case**: Clean up unused security groups for better security posture.

---

## Capacity Tools

### 9. find_underutilized_ec2_instances

**Purpose**: Find EC2 instances with low CPU and memory utilization (≤20%).

**Parameters**:
- `region_name` (str, default: "us-east-1"): AWS region
- `period` (int, default: 30): Lookback period in days
- `max_results` (int, default: 100): Maximum results
- Plus authentication parameters

**Returns**:
```json
{
  "id": 109,
  "name": "Underutilized EC2 Instances",
  "count": 5,
  "resource": [
    {
      "InstanceId": "i-12345678",
      "InstanceName": "web-server-1",
      "InstanceType": "t3.large",
      "VpcId": "vpc-12345678",
      "AvailabilityZone": "us-east-1a",
      "Vcpu": 2,
      "MemoryGiB": "8.0",
      "AvgCPUUtilization": 5.2,
      "MaxCPUUtilization": 15.0,
      "MaxMemoryUtilization": 18.0,
      "Description": "Instance is underutilized. Consider downsizing to save costs."
    }
  ]
}
```

**Use Case**: Downsize underutilized instances to save 30-50% on compute costs.

---

### 10. find_overutilized_ec2_instances

**Purpose**: Find EC2 instances with high CPU or memory utilization (≥80%).

**Parameters**:
- `region_name` (str, default: "us-east-1"): AWS region
- `period` (int, default: 30): Lookback period in days
- `max_results` (int, default: 100): Maximum results
- Plus authentication parameters

**Returns**:
```json
{
  "id": 111,
  "name": "Overutilized EC2 Instances",
  "count": 3,
  "resource": [
    {
      "InstanceId": "i-87654321",
      "InstanceName": "api-server-1",
      "InstanceType": "t3.small",
      "VpcId": "vpc-12345678",
      "AvailabilityZone": "us-east-1b",
      "Vcpu": 2,
      "MemoryGiB": "2.0",
      "AvgCPUUtilization": 75.5,
      "MaxCPUUtilization": 95.0,
      "MaxMemoryUtilization": 88.0,
      "Description": "Instance is overutilized. Consider upsizing for better performance."
    }
  ]
}
```

**Use Case**: Upsize overutilized instances to prevent performance issues.

---

### 11. find_underutilized_rds_instances

**Purpose**: Find RDS instances with low CPU utilization (≤20%).

**Parameters**:
- `region_name` (str, default: "us-east-1"): AWS region
- `period` (int, default: 30): Lookback period in days
- `max_results` (int, default: 100): Maximum results
- Plus authentication parameters

**Returns**:
```json
{
  "id": 110,
  "name": "Underutilized RDS Instances",
  "count": 2,
  "resource": [
    {
      "InstanceName": "prod-db",
      "InstanceType": "db.r5.xlarge",
      "Engine": "postgres",
      "EngineVersion": "14.7",
      "AvailabilityZone": "us-east-1a",
      "MultiAZ": true,
      "AvgCPUUtilization": 8.5,
      "MaxCPUUtilization": 15.0,
      "Description": "RDS instance with low CPU utilization (≤20%) in the last 30 days"
    }
  ]
}
```

**Use Case**: Downsize underutilized RDS instances to save on database costs.

---

### 12. find_overutilized_rds_instances

**Purpose**: Find RDS instances with high CPU utilization (≥80%).

**Parameters**:
- `region_name` (str, default: "us-east-1"): AWS region
- `period` (int, default: 30): Lookback period in days
- `max_results` (int, default: 100): Maximum results
- Plus authentication parameters

**Returns**:
```json
{
  "id": 112,
  "name": "Overutilized RDS Instances",
  "count": 1,
  "resource": [
    {
      "InstanceName": "analytics-db",
      "InstanceType": "db.t3.medium",
      "Engine": "mysql",
      "EngineVersion": "8.0.32",
      "AvailabilityZone": "us-east-1b",
      "MultiAZ": false,
      "AvgCPUUtilization": 78.5,
      "MaxCPUUtilization": 92.0,
      "Description": "RDS instance with high CPU utilization (≥80%) in the last 30 days"
    }
  ]
}
```

**Use Case**: Upsize overutilized RDS instances to prevent database slowdowns.

---

## Cost Optimization Tools

### 13. get_all_cost_optimization_recommendations

**Purpose**: Get all cost optimization recommendations from AWS Cost Optimization Hub (19 resource types).

**Parameters**:
- `region_name` (str, optional): Filter by AWS region
- Plus authentication parameters

**Returns**: List of 19 resource type objects

**Use Case**: Comprehensive cost optimization analysis across all AWS services.

---

### 14. get_cost_optimization_ec2

**Purpose**: Get EC2 instance cost optimization recommendations.

**Parameters**:
- `region_name` (str, optional): Filter by AWS region
- Plus authentication parameters

**Returns**:
```json
{
  "id": 201,
  "name": "Cost_Ec2Instance",
  "count": 10,
  "resource": [
    {
      "RecommendationId": "rec-12345",
      "AccountId": "123456789012",
      "Region": "us-east-1",
      "ResourceId": "i-12345678",
      "ResourceArn": "arn:aws:ec2:us-east-1:123456789012:instance/i-12345678",
      "CurrentResourceType": "Ec2Instance",
      "RecommendedResourceType": "Ec2Instance",
      "EstimatedMonthlySavings": 45.50,
      "EstimatedSavingsPercentage": 30.0,
      "EstimatedMonthlyCost": 151.67,
      "CurrencyCode": "USD",
      "ImplementationEffort": "Low",
      "RestartNeeded": true,
      "ActionType": "Rightsize",
      "RollbackPossible": true,
      "CurrentResourceSummary": "t3.large",
      "RecommendedResourceSummary": "t3.medium",
      "LastRefreshTimestamp": "2024-01-15T10:30:00Z",
      "RecommendationLookbackPeriodInDays": 14,
      "Source": "ComputeOptimizer",
      "Description": "Cost optimization: Rightsize for Ec2Instance"
    }
  ]
}
```

**Use Case**: AWS-recommended EC2 instance optimizations based on actual usage.

---

### 15. get_cost_optimization_lambda

**Purpose**: Get Lambda function cost optimization recommendations.

**Parameters**: Same as EC2

**Returns**: Similar structure with Lambda-specific recommendations

**Use Case**: Optimize Lambda memory allocation and architecture.

---

### 16. get_cost_optimization_rds

**Purpose**: Get RDS instance cost optimization recommendations.

**Parameters**: Same as EC2

**Returns**: Similar structure with RDS-specific recommendations

**Use Case**: Optimize RDS instance types and storage configurations.

---

### 17. get_cost_optimization_ebs

**Purpose**: Get EBS volume cost optimization recommendations.

**Parameters**: Same as EC2

**Returns**: Similar structure with EBS-specific recommendations

**Use Case**: Optimize EBS volume types (gp2 → gp3, etc.).

---

## Application Performance Tools

### 18. find_target_groups_with_high_error_rate

**Purpose**: Find target groups with high 5XX error rates.

**Parameters**:
- `region_name` (str, default: "us-east-1"): AWS region
- `period` (int, default: 7): Lookback period in days
- `error_threshold` (float, default: 5.0): Error rate threshold percentage
- Plus authentication parameters

**Returns**:
```json
{
  "id": 115,
  "name": "Target Group Error Rate",
  "count": 2,
  "resource": [
    {
      "TargetGroupName": "api-tg",
      "LoadBalancer": "api-alb",
      "Protocol": "HTTP",
      "Port": 80,
      "TotalRequests": 1000000,
      "Total5XXErrors": 75000,
      "ErrorRate": "7.50%",
      "Description": "Target group has 7.50% error rate (threshold: 5.0%)"
    }
  ]
}
```

**Use Case**: Identify application health issues causing high error rates.

---

### 19. find_target_groups_with_high_response_time

**Purpose**: Find target groups with high response times.

**Parameters**:
- `region_name` (str, default: "us-east-1"): AWS region
- `period` (int, default: 7): Lookback period in days
- `response_time_threshold` (float, default: 1.0): Threshold in seconds
- Plus authentication parameters

**Returns**:
```json
{
  "id": 116,
  "name": "Target Group Response Time",
  "count": 3,
  "resource": [
    {
      "TargetGroupName": "slow-api-tg",
      "LoadBalancer": "api-alb",
      "Protocol": "HTTP",
      "Port": 80,
      "AvgResponseTime": "2.500s",
      "MaxResponseTime": "5.000s",
      "Threshold": "1.0s",
      "Description": "Target group has 2.500s avg response time (threshold: 1.0s)"
    }
  ]
}
```

**Use Case**: Identify performance bottlenecks in applications.

---

## Upgrade Tools

### 20. find_asgs_with_old_amis

**Purpose**: Find Auto Scaling Groups using AMIs older than the specified period.

**Parameters**:
- `region_name` (str, default: "us-east-1"): AWS region
- `period` (int, default: 90): Minimum age in days
- `max_results` (int, default: 100): Maximum results
- Plus authentication parameters

**Returns**:
```json
{
  "id": 113,
  "name": "ASGs with Old AMIs",
  "count": 5,
  "resource": [
    {
      "AutoScalingGroupName": "web-asg",
      "AMIId": "ami-12345678",
      "AMIName": "web-app-v1.0",
      "AMICreationDate": "2023-01-01T00:00:00.000Z",
      "AMIAge": "365 days",
      "Platform": "Linux/UNIX",
      "MinSize": 2,
      "MaxSize": 10,
      "DesiredCapacity": 4,
      "Description": "ASG using AMI that is 365 days old (threshold: 90 days)"
    }
  ]
}
```

**Use Case**: Identify ASGs that need AMI updates for security and performance.

---

## Common Parameters

All tools accept these authentication parameters:

- `profile_name` (str, optional): AWS profile name
- `role_arn` (str, optional): IAM role ARN to assume
- `access_key` (str, optional): AWS access key ID
- `secret_access_key` (str, optional): AWS secret access key
- `session_token` (str, optional): AWS session token for temporary credentials

## Response Format

All tools return a standardized response:

```python
{
    "id": int,              # Unique tool ID (101-219)
    "name": str,            # Human-readable tool name
    "fields": dict,         # Field ID to accessor mapping
    "headers": list,        # Header definitions for display
    "count": int,           # Number of resources found
    "resource": list        # List of resource dictionaries
}
```

## Tool IDs

- **101-108**: Cleanup tools
- **109-112**: Capacity tools
- **113**: Upgrade tools
- **114**: Additional cleanup (Security Groups)
- **115-116**: Application performance tools
- **201-219**: Cost optimization tools (by resource type)
