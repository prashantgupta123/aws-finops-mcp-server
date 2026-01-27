# Category Use Cases & Combinations

## Common Scenarios

### 1. Monthly Cost Review Meeting
**Goal**: Identify cost savings opportunities

```bash
MCP_TOOL_CATEGORIES="cost,cleanup,capacity"
```

**What you get** (34 tools):
- Cost analysis and trends
- Unused resources to delete
- Over/under-utilized resources to right-size

**Typical workflow**:
1. Run `get_daily_cost_trend` to see spending patterns
2. Run `get_cost_by_service` to identify top spenders
3. Run cleanup tools to find deletable resources
4. Run capacity tools to find right-sizing opportunities

---

### 2. Security Compliance Audit
**Goal**: Ensure security best practices

```bash
MCP_TOOL_CATEGORIES="security,governance"
```

**What you get** (8 tools):
- Unencrypted resources
- Public S3 buckets
- Overly permissive security groups
- Untagged resources
- Tag compliance analysis

**Typical workflow**:
1. Run `find_unencrypted_*` tools
2. Run `find_public_s3_buckets`
3. Run `find_overly_permissive_security_groups`
4. Run `analyze_tag_compliance`

---

### 3. Performance Optimization Sprint
**Goal**: Improve application performance

```bash
MCP_TOOL_CATEGORIES="performance,capacity,application"
```

**What you get** (16 tools):
- Lambda cold start analysis
- API Gateway performance
- DynamoDB throttling
- RDS Performance Insights
- CloudFront cache hit ratios
- Resource utilization metrics
- Application health checks

**Typical workflow**:
1. Run `analyze_lambda_cold_starts`
2. Run `analyze_api_gateway_performance`
3. Run `find_overutilized_*` tools
4. Run `find_target_groups_with_high_response_time`

---

### 4. Quarterly Infrastructure Cleanup
**Goal**: Remove unused resources

```bash
MCP_TOOL_CATEGORIES="cleanup,network,storage,containers,messaging,monitoring"
```

**What you get** (26 tools):
- All cleanup tools
- Network resource cleanup
- Storage optimization
- Container cleanup
- Messaging cleanup
- Monitoring cleanup

**Typical workflow**:
1. Run all `find_unused_*` tools
2. Review results by cost impact
3. Tag resources for deletion
4. Schedule cleanup

---

### 5. Modernization Project
**Goal**: Upgrade outdated resources

```bash
MCP_TOOL_CATEGORIES="upgrade,security"
```

**What you get** (13 tools):
- Outdated AMIs, runtimes, engines
- Old generation instance types
- Security compliance checks

**Typical workflow**:
1. Run `find_outdated_*` tools
2. Prioritize by security impact
3. Plan upgrade schedule
4. Verify security compliance

---

### 6. New AWS Account Setup
**Goal**: Establish governance and cost controls

```bash
MCP_TOOL_CATEGORIES="governance,cost,security"
```

**What you get** (24 tools):
- Tagging compliance
- Cost allocation
- Security best practices
- Cost optimization recommendations

**Typical workflow**:
1. Run `analyze_tag_compliance`
2. Run `find_untagged_resources`
3. Run security compliance checks
4. Set up cost monitoring

---

### 7. Incident Response
**Goal**: Quickly identify performance issues

```bash
MCP_TOOL_CATEGORIES="performance,application,monitoring"
```

**What you get** (10 tools):
- Performance metrics
- Application health
- Monitoring insights

**Typical workflow**:
1. Run `find_target_groups_with_high_error_rate`
2. Run `analyze_rds_performance_insights`
3. Run `analyze_dynamodb_throttling`
4. Check CloudWatch alarms

---

### 8. Budget Planning
**Goal**: Forecast and optimize costs

```bash
MCP_TOOL_CATEGORIES="cost"
```

**What you get** (16 tools):
- Cost trends and breakdowns
- Savings recommendations
- Reserved Instance analysis
- Storage optimization

**Typical workflow**:
1. Run `get_daily_cost_trend`
2. Run `get_cost_by_region_and_service`
3. Run `get_savings_plans_recommendations`
4. Run `analyze_reserved_instance_utilization`

---

### 9. Container Platform Optimization
**Goal**: Optimize ECS/EKS resources

```bash
MCP_TOOL_CATEGORIES="containers,capacity,upgrade"
```

**What you get** (21 tools):
- Container resource cleanup
- ECS/EKS utilization
- Outdated platform versions

**Typical workflow**:
1. Run `find_unused_ecs_clusters_and_services`
2. Run `find_underutilized_ecs_services`
3. Run `find_outdated_eks_cluster_versions`
4. Run `find_old_ecs_task_definitions`

---

### 10. Database Optimization
**Goal**: Optimize database resources

```bash
MCP_TOOL_CATEGORIES="database,capacity,upgrade,performance"
```

**What you get** (22 tools):
- Database utilization
- Outdated engine versions
- Performance insights
- Throttling analysis

**Typical workflow**:
1. Run `find_unused_dynamodb_tables`
2. Run `find_underutilized_rds_instances`
3. Run `find_outdated_rds_engine_versions`
4. Run `analyze_rds_performance_insights`

---

## Category Combinations by Team

### FinOps Team
```bash
MCP_TOOL_CATEGORIES="cost,cleanup,capacity,governance"
```
Focus: Cost optimization, resource cleanup, right-sizing, governance

### Security Team
```bash
MCP_TOOL_CATEGORIES="security,governance,upgrade"
```
Focus: Security compliance, tagging, outdated resources

### DevOps Team
```bash
MCP_TOOL_CATEGORIES="performance,capacity,monitoring,application"
```
Focus: Performance, utilization, monitoring, health

### Platform Team
```bash
MCP_TOOL_CATEGORIES="containers,network,storage,database"
```
Focus: Infrastructure management and optimization

### All Teams (Default)
```bash
MCP_TOOL_CATEGORIES="all"
```
Access to all 76 tools

---

## Tips

1. **Start Small**: Begin with 1-2 categories, expand as needed
2. **Combine Related**: Group categories by use case
3. **Multiple Configs**: Set up different MCP server instances for different teams
4. **Review Documentation**: Check [TOOL_CATEGORIES.md](TOOL_CATEGORIES.md) for complete category details
5. **Document**: Share your category combinations with your team
