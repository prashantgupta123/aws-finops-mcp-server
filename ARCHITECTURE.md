# AWS FinOps MCP Server - Architecture

## Overview

The AWS FinOps MCP Server is a Model Context Protocol (MCP) server built with FastMCP that provides comprehensive AWS financial operations tools. It enables AI assistants and automation tools to analyze AWS resources for cost optimization, capacity planning, cleanup opportunities, and performance monitoring.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    MCP Client (Kiro, etc.)                  │
└────────────────────────┬────────────────────────────────────┘
                         │ MCP Protocol
                         │
┌────────────────────────▼────────────────────────────────────┐
│                  FastMCP Server (server.py)                 │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Tool Definitions (23 tools)             │   │
│  │  - Cleanup (9)  - Capacity (4)  - Cost (5)          │   │
│  │  - Application (2)  - Upgrade (1)                    │   │
│  └──────────────────────┬───────────────────────────────┘   │
└─────────────────────────┼───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                  Session Management                         │
│                    (session.py)                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  - Profile Auth    - Role Assumption                 │   │
│  │  - Access Keys     - Temporary Credentials           │   │
│  └──────────────────────┬───────────────────────────────┘   │
└─────────────────────────┼───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                    Tool Modules                             │
│  ┌──────────────┬──────────────┬──────────────┬─────────┐   │
│  │  cleanup.py  │ capacity.py  │   cost.py    │  app.py │   │
│  │              │              │              │         │   │
│  │ - Lambda     │ - EC2 Under  │ - EC2 Cost   │ - Error │   │
│  │ - EIP        │ - EC2 Over   │ - Lambda     │ - Resp  │   │
│  │ - AMI        │ - RDS Under  │ - RDS Cost   │   Time  │   │
│  │ - LB         │ - RDS Over   │ - EBS Cost   │         │   │
│  │ - TG         │              │ - All Cost   │         │   │
│  │ - Logs       │              │              │         │   │
│  │ - Snapshots  │              │              │         │   │
│  │ - SG         │              │              │         │   │
│  └──────────────┴──────────────┴──────────────┴─────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                  upgrade.py                          │   │
│  │                - ASG Old AMIs                        │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                   Utility Modules                           │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  helpers.py - Field formatting, data normalization   │   │
│  │  metrics.py - CloudWatch metric calculations         │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                      AWS Services                           │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  EC2  RDS  Lambda  ELB  CloudWatch  Logs  Cost Hub  │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. FastMCP Server (`server.py`)

**Responsibility**: MCP protocol implementation and tool registration

**Key Features**:
- 23 tool definitions with comprehensive docstrings
- Standardized parameter handling (credentials, region, period, etc.)
- Automatic session creation from credentials
- Type hints for all parameters

**Tool Categories**:
- **Cleanup** (9 tools): Identify unused resources
- **Capacity** (4 tools): Analyze resource utilization
- **Cost** (5 tools): Cost optimization recommendations
- **Application** (2 tools): Performance monitoring
- **Upgrade** (1 tool): Outdated configuration detection

### 2. Session Management (`session.py`)

**Responsibility**: AWS authentication and session creation

**Supported Auth Methods**:
1. **Profile-based**: Uses AWS CLI profiles
2. **Role Assumption**: Assumes IAM roles via STS
3. **Access Keys**: Direct credential authentication
4. **Temporary Credentials**: Session token support
5. **Default Chain**: Falls back to environment/instance profile

**Key Functions**:
- `get_aws_session()`: Main entry point for session creation
- `_create_assumed_role_session()`: Internal role assumption logic

### 3. Tool Modules

#### cleanup.py
**Purpose**: Identify unused AWS resources for cost savings

**Tools**:
- `find_unused_lambda_functions()`: No invocations in period
- `find_unused_elastic_ips()`: Unattached EIPs
- `find_unused_amis()`: AMIs not used by instances/ASGs
- `find_unused_load_balancers()`: No traffic in period
- `find_unused_target_groups()`: No registered targets
- `find_unused_log_groups()`: No recent log events
- `find_unused_snapshots()`: Not associated with AMIs/volumes
- `find_unused_security_groups()`: Not attached to resources

**Common Pattern**:
```python
def find_unused_X(session, region_name, period, max_results):
    # 1. Get all resources of type X
    # 2. Check usage metrics (CloudWatch, associations, etc.)
    # 3. Filter based on criteria
    # 4. Return standardized response
```

#### capacity.py
**Purpose**: Analyze resource utilization for right-sizing

**Tools**:
- `find_underutilized_ec2_instances()`: CPU ≤20% AND Memory ≤20%
- `find_overutilized_ec2_instances()`: CPU ≥80% OR Memory ≥80%
- `find_underutilized_rds_instances()`: CPU ≤20%
- `find_overutilized_rds_instances()`: CPU ≥80%

**Metrics Used**:
- CloudWatch CPU utilization (AWS/EC2, AWS/RDS)
- CloudWatch memory utilization (CWAgent)
- 1-day period aggregation
- Average, Min, Max calculations

#### cost.py
**Purpose**: AWS Cost Optimization Hub integration

**Tools**:
- `get_all_cost_optimization_recommendations()`: All 19 resource types
- `get_cost_optimization_ec2()`: EC2-specific recommendations
- `get_cost_optimization_lambda()`: Lambda-specific recommendations
- `get_cost_optimization_rds()`: RDS-specific recommendations
- `get_cost_optimization_ebs()`: EBS-specific recommendations

**Resource Types Supported** (19 total):
- Compute: EC2, Lambda, ECS, ASG
- Storage: EBS, RDS Storage, Aurora Storage
- Database: RDS, DynamoDB, MemoryDB
- Savings: Savings Plans, Reserved Instances
- Network: NAT Gateway
- Search: OpenSearch, Redshift, ElastiCache

#### application.py
**Purpose**: Application performance monitoring

**Tools**:
- `find_target_groups_with_high_error_rate()`: 5XX errors ≥ threshold
- `find_target_groups_with_high_response_time()`: Response time ≥ threshold

**Metrics Used**:
- HTTPCode_Target_5XX_Count
- RequestCount
- TargetResponseTime

#### upgrade.py
**Purpose**: Identify outdated configurations

**Tools**:
- `find_asgs_with_old_amis()`: ASGs using AMIs older than period

### 4. Utility Modules

#### helpers.py
**Functions**:
- `format_header()`: Convert field names to readable headers
- `fields_to_headers()`: Generate header list from field dict
- `normalize_data()`: Ensure consistent data structure
- `safe_float()`: Safe type conversion
- `remove_percent_sign()`: Clean percentage values

#### metrics.py
**Functions**:
- `calculate_metrics()`: Average, min, max from datapoints
- `calculate_memory_metrics_gb()`: Convert bytes to GB
- `get_metric_statistics()`: CloudWatch metric retrieval

## Data Flow

### 1. Tool Invocation
```
MCP Client → FastMCP Server → Tool Function
```

### 2. Session Creation
```
Tool Function → create_session() → get_aws_session() → boto3.Session
```

### 3. AWS API Calls
```
Tool Function → AWS Client → AWS Service API
```

### 4. Data Processing
```
AWS Response → Tool Logic → Standardized Format → MCP Client
```

## Standardized Response Format

All tools return a consistent structure:

```python
{
    "id": int,              # Unique tool ID
    "name": str,            # Human-readable name
    "fields": dict,         # Field ID to accessor mapping
    "headers": list,        # Header definitions
    "count": int,           # Number of resources found
    "resource": list        # List of resource dictionaries
}
```

## Error Handling

### Session Creation
- Invalid credentials → Exception with clear message
- Role assumption failure → STS error propagation
- Network issues → boto3 exception handling

### Tool Execution
- Missing permissions → AWS API error
- Invalid region → boto3 validation error
- No resources found → Empty list (count=0)
- Partial failures → Logged, continue processing

## Performance Considerations

### Pagination
- All list operations use pagination
- Configurable `max_results` parameter
- NextToken/Marker handling

### Parallel Processing
- Tools are independent (can run in parallel)
- No shared state between tools
- Session reuse within tool execution

### CloudWatch Metrics
- 1-day period for aggregation
- Batch metric retrieval where possible
- Configurable lookback period

## Security

### Credentials
- Never logged or exposed
- Temporary credentials supported
- Role assumption with session naming

### Permissions
- Read-only operations only
- Least privilege principle
- No resource modification

### Data
- No PII collection
- Resource metadata only
- No sensitive data storage

## Extensibility

### Adding New Tools

1. **Create tool function** in appropriate module:
```python
def find_new_resource(session, region_name, period, max_results):
    # Implementation
    return standardized_response
```

2. **Register in server.py**:
```python
@mcp.tool()
def find_new_resource(
    region_name: str = "us-east-1",
    period: int = 90,
    # ... credential parameters
) -> dict[str, Any]:
    """Tool description."""
    session = create_session(...)
    return module.find_new_resource(session, region_name, period)
```

3. **Update documentation**:
- Add to README.md
- Add example to tool_usage.md
- Update tool count

### Adding New Resource Types

1. Add to `RESOURCE_TYPES_CONFIG` in `cost.py`
2. Update documentation
3. No code changes needed (dynamic processing)

## Testing Strategy

### Unit Tests
- Session creation with different auth methods
- Helper function correctness
- Metric calculations

### Integration Tests
- Mock AWS API responses
- End-to-end tool execution
- Error handling scenarios

### Manual Testing
- Real AWS account testing
- Multi-region validation
- Performance benchmarking

## Deployment

### Package Installation
```bash
pip install .
```

### MCP Configuration
```json
{
  "mcpServers": {
    "aws-finops": {
      "command": "python",
      "args": ["-m", "aws_finops_mcp"]
    }
  }
}
```

### Environment Variables
- `AWS_PROFILE`: Default profile
- `AWS_REGION`: Default region
- `AWS_ACCESS_KEY_ID`: Access key
- `AWS_SECRET_ACCESS_KEY`: Secret key

## Future Enhancements

### Planned Features
1. **More cleanup tools**: ECS tasks, CloudFormation stacks, etc.
2. **Cost forecasting**: Trend analysis and predictions
3. **Automated remediation**: Safe resource cleanup
4. **Multi-account support**: Organization-wide analysis
5. **Custom thresholds**: User-defined utilization limits
6. **Reporting**: PDF/Excel report generation
7. **Scheduling**: Periodic analysis automation

### Performance Improvements
1. **Caching**: Session and resource caching
2. **Async operations**: Parallel AWS API calls
3. **Incremental updates**: Delta-based analysis
4. **Result streaming**: Large dataset handling

## Dependencies

### Core
- `mcp>=1.0.0`: MCP protocol implementation
- `boto3>=1.35.0`: AWS SDK
- `botocore>=1.35.0`: AWS core library

### Development
- `pytest>=8.0.0`: Testing framework
- `pytest-asyncio>=0.23.0`: Async test support
- `black>=24.0.0`: Code formatting
- `ruff>=0.3.0`: Linting

## Version History

### v0.1.0 (Current)
- Initial release
- 23 tools across 5 categories
- FastMCP implementation
- Comprehensive documentation
