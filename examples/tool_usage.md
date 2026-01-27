# AWS FinOps MCP Server - Tool Usage Examples

## Authentication Methods

### 1. Using AWS Profile
```json
{
  "tool": "find_unused_lambda_functions",
  "arguments": {
    "profile_name": "production",
    "region_name": "us-west-2",
    "period": 90
  }
}
```

### 2. Using IAM Role (Assume Role)
```json
{
  "tool": "find_underutilized_ec2_instances",
  "arguments": {
    "role_arn": "arn:aws:iam::123456789012:role/FinOpsRole",
    "region_name": "us-east-1",
    "period": 30
  }
}
```

### 3. Using Access Keys
```json
{
  "tool": "get_cost_optimization_ec2",
  "arguments": {
    "access_key": "AKIAIOSFODNN7EXAMPLE",
    "secret_access_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
    "region_name": "us-east-1"
  }
}
```

### 4. Using Temporary Credentials
```json
{
  "tool": "find_unused_elastic_ips",
  "arguments": {
    "access_key": "ASIAIOSFODNN7EXAMPLE",
    "secret_access_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
    "session_token": "FwoGZXIvYXdzEBYaD...",
    "region_name": "us-west-2"
  }
}
```

## Cleanup Tools

### Find Unused Lambda Functions
```json
{
  "tool": "find_unused_lambda_functions",
  "arguments": {
    "profile_name": "production",
    "region_name": "us-east-1",
    "period": 90,
    "max_results": 100
  }
}
```

### Find Unused Elastic IPs
```json
{
  "tool": "find_unused_elastic_ips",
  "arguments": {
    "profile_name": "production",
    "region_name": "us-east-1"
  }
}
```

### Find Unused AMIs
```json
{
  "tool": "find_unused_amis",
  "arguments": {
    "profile_name": "production",
    "region_name": "us-east-1",
    "period": 90,
    "max_results": 100
  }
}
```

### Find Unused Load Balancers
```json
{
  "tool": "find_unused_load_balancers",
  "arguments": {
    "profile_name": "production",
    "region_name": "us-east-1",
    "period": 90
  }
}
```

### Find Unused Security Groups
```json
{
  "tool": "find_unused_security_groups",
  "arguments": {
    "profile_name": "production",
    "region_name": "us-east-1",
    "max_results": 100
  }
}
```

## Capacity Tools

### Find Underutilized EC2 Instances
```json
{
  "tool": "find_underutilized_ec2_instances",
  "arguments": {
    "profile_name": "production",
    "region_name": "us-east-1",
    "period": 30,
    "max_results": 100
  }
}
```

### Find Overutilized EC2 Instances
```json
{
  "tool": "find_overutilized_ec2_instances",
  "arguments": {
    "profile_name": "production",
    "region_name": "us-east-1",
    "period": 30,
    "max_results": 100
  }
}
```

### Find Underutilized RDS Instances
```json
{
  "tool": "find_underutilized_rds_instances",
  "arguments": {
    "profile_name": "production",
    "region_name": "us-east-1",
    "period": 30,
    "max_results": 100
  }
}
```

### Find Overutilized RDS Instances
```json
{
  "tool": "find_overutilized_rds_instances",
  "arguments": {
    "profile_name": "production",
    "region_name": "us-east-1",
    "period": 30,
    "max_results": 100
  }
}
```

## Cost Optimization Tools

### Get All Cost Optimization Recommendations
```json
{
  "tool": "get_all_cost_optimization_recommendations",
  "arguments": {
    "profile_name": "production",
    "region_name": "us-east-1"
  }
}
```

### Get EC2 Cost Optimization
```json
{
  "tool": "get_cost_optimization_ec2",
  "arguments": {
    "profile_name": "production",
    "region_name": "us-east-1"
  }
}
```

### Get Lambda Cost Optimization
```json
{
  "tool": "get_cost_optimization_lambda",
  "arguments": {
    "profile_name": "production",
    "region_name": "us-west-2"
  }
}
```

### Get RDS Cost Optimization
```json
{
  "tool": "get_cost_optimization_rds",
  "arguments": {
    "profile_name": "production",
    "region_name": "us-east-1"
  }
}
```

### Get EBS Cost Optimization
```json
{
  "tool": "get_cost_optimization_ebs",
  "arguments": {
    "profile_name": "production",
    "region_name": "us-east-1"
  }
}
```

## Application Performance Tools

### Find Target Groups with High Error Rate
```json
{
  "tool": "find_target_groups_with_high_error_rate",
  "arguments": {
    "profile_name": "production",
    "region_name": "us-east-1",
    "period": 7,
    "error_threshold": 5.0
  }
}
```

### Find Target Groups with High Response Time
```json
{
  "tool": "find_target_groups_with_high_response_time",
  "arguments": {
    "profile_name": "production",
    "region_name": "us-east-1",
    "period": 7,
    "response_time_threshold": 1.0
  }
}
```

## Upgrade Tools

### Find ASGs with Old AMIs
```json
{
  "tool": "find_asgs_with_old_amis",
  "arguments": {
    "profile_name": "production",
    "region_name": "us-east-1",
    "period": 90,
    "max_results": 100
  }
}
```

## Response Format

All tools return a standardized response format:

```json
{
  "id": 101,
  "name": "Unused Lambda Functions",
  "fields": {
    "1": "FunctionName",
    "2": "Runtime",
    "3": "MemorySize",
    "4": "LastModified",
    "5": "Description"
  },
  "headers": [
    {"Header": "Function Name", "accessor": "FunctionName"},
    {"Header": "Runtime", "accessor": "Runtime"},
    {"Header": "Memory Size", "accessor": "MemorySize"},
    {"Header": "Last Modified", "accessor": "LastModified"},
    {"Header": "Description", "accessor": "Description"}
  ],
  "count": 5,
  "resource": [
    {
      "FunctionName": "old-function-1",
      "Runtime": "python3.8",
      "MemorySize": 128,
      "LastModified": "2023-01-15T10:30:00.000+0000",
      "Description": "Lambda function not invoked in the last 90 days"
    }
  ]
}
```

## Multi-Region Analysis

To analyze multiple regions, call the tools multiple times with different region names:

```json
[
  {
    "tool": "find_unused_lambda_functions",
    "arguments": {
      "profile_name": "production",
      "region_name": "us-east-1",
      "period": 90
    }
  },
  {
    "tool": "find_unused_lambda_functions",
    "arguments": {
      "profile_name": "production",
      "region_name": "us-west-2",
      "period": 90
    }
  },
  {
    "tool": "find_unused_lambda_functions",
    "arguments": {
      "profile_name": "production",
      "region_name": "eu-west-1",
      "period": 90
    }
  }
]
```
