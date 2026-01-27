# IAM Policies for AWS FinOps MCP Server

This directory contains IAM policy templates for different use cases and security requirements.

## 📋 Available Policies

### 1. Full Policy (Recommended)
**File**: `finops-full-policy.json`

**Use Case**: Production environments with all 24 tools enabled

**Permissions**:
- ✅ EC2 (instances, AMIs, snapshots, EIPs, security groups)
- ✅ RDS (instances, clusters, snapshots)
- ✅ Lambda (functions, configurations)
- ✅ ELB (load balancers, target groups)
- ✅ Auto Scaling (groups, launch configs)
- ✅ CloudWatch (metrics, alarms)
- ✅ CloudWatch Logs (log groups, streams)
- ✅ Cost Explorer (costs, forecasts)
- ✅ Cost Optimization Hub (recommendations)
- ✅ STS (assume role, get caller identity)
- ✅ Tags (resource tagging)

**Tools Enabled**: All 24 tools

---

### 2. Minimal Policy
**File**: `finops-minimal-policy.json`

**Use Case**: Testing or limited scope deployments

**Permissions**:
- Basic describe/list permissions for all services
- Cost Explorer read access
- Cost Optimization Hub read access
- STS GetCallerIdentity

**Tools Enabled**: All 24 tools (with basic permissions)

---

### 3. Read-Only Policy
**File**: `finops-readonly-policy.json`

**Use Case**: Maximum security with read-only access

**Permissions**:
- All Describe*, Get*, List* actions
- Full Cost Explorer access
- Full Cost Optimization Hub access
- No write permissions

**Tools Enabled**: All 24 tools

---

### 4. Cost-Only Policy
**File**: `finops-cost-only-policy.json`

**Use Case**: Cost analysis and optimization only

**Permissions**:
- Cost Explorer (all read operations)
- Cost Optimization Hub (all read operations)
- Savings Plans and Reserved Instances data
- STS GetCallerIdentity

**Tools Enabled**: 9 tools (Cost Explorer + Cost Optimization)

---

### 5. Cross-Account Role Trust Policy
**File**: `finops-cross-account-role.json`

**Use Case**: Multi-account deployments

**Configuration**:
- Replace `MANAGEMENT_ACCOUNT_ID` with your management account ID
- Replace `finops-mcp-server-unique-id` with your unique external ID
- Attach one of the permission policies above to this role

---

## 🚀 Quick Setup

### Option 1: AWS Console

1. **Go to IAM Console** → Policies → Create Policy
2. **Select JSON tab**
3. **Copy and paste** one of the policy files
4. **Review and create** with a descriptive name
5. **Attach to user/role** that runs the MCP server

### Option 2: AWS CLI

```bash
# Create policy
aws iam create-policy \
  --policy-name FinOpsFullPolicy \
  --policy-document file://iam-policies/finops-full-policy.json \
  --description "Full permissions for AWS FinOps MCP Server"

# Attach to user
aws iam attach-user-policy \
  --user-name finops-user \
  --policy-arn arn:aws:iam::ACCOUNT_ID:policy/FinOpsFullPolicy

# Or attach to role
aws iam attach-role-policy \
  --role-name finops-role \
  --policy-arn arn:aws:iam::ACCOUNT_ID:policy/FinOpsFullPolicy
```

### Option 3: Terraform

```hcl
resource "aws_iam_policy" "finops_full" {
  name        = "FinOpsFullPolicy"
  description = "Full permissions for AWS FinOps MCP Server"
  policy      = file("${path.module}/iam-policies/finops-full-policy.json")
}

resource "aws_iam_role_policy_attachment" "finops_attach" {
  role       = aws_iam_role.finops_role.name
  policy_arn = aws_iam_policy.finops_full.arn
}
```

### Option 4: CloudFormation

```yaml
Resources:
  FinOpsPolicy:
    Type: AWS::IAM::Policy
    Properties:
      PolicyName: FinOpsFullPolicy
      PolicyDocument: !Sub |
        ${file://iam-policies/finops-full-policy.json}
      Roles:
        - !Ref FinOpsRole
```

---

## 🔒 Security Best Practices

### 1. Principle of Least Privilege
- Start with **minimal-policy.json**
- Add permissions as needed
- Remove unused permissions

### 2. Use IAM Roles (Recommended)
```bash
# For EC2
aws iam create-role --role-name finops-ec2-role \
  --assume-role-policy-document file://ec2-trust-policy.json

# For ECS
aws iam create-role --role-name finops-ecs-role \
  --assume-role-policy-document file://ecs-trust-policy.json
```

### 3. Enable CloudTrail
Monitor all API calls made by the MCP server:
```bash
aws cloudtrail create-trail \
  --name finops-audit-trail \
  --s3-bucket-name finops-audit-logs
```

### 4. Use External ID for Cross-Account
When using cross-account roles, always use an external ID:
```json
{
  "Condition": {
    "StringEquals": {
      "sts:ExternalId": "your-unique-external-id"
    }
  }
}
```

### 5. Rotate Credentials Regularly
- Use temporary credentials when possible
- Rotate access keys every 90 days
- Use AWS Secrets Manager for key storage

---

## 📊 Policy Comparison

| Feature | Full | Minimal | Read-Only | Cost-Only |
|---------|------|---------|-----------|-----------|
| **EC2 Analysis** | ✅ | ✅ | ✅ | ❌ |
| **RDS Analysis** | ✅ | ✅ | ✅ | ❌ |
| **Lambda Analysis** | ✅ | ✅ | ✅ | ❌ |
| **Cost Explorer** | ✅ | ✅ | ✅ | ✅ |
| **Cost Optimization** | ✅ | ✅ | ✅ | ✅ |
| **CloudWatch Metrics** | ✅ | ✅ | ✅ | ❌ |
| **Tag Management** | ✅ | ❌ | ✅ | ❌ |
| **Cross-Account** | ✅ | ✅ | ✅ | ✅ |
| **Tools Enabled** | 24 | 24 | 24 | 9 |

---

## 🎯 Recommended Policies by Use Case

### Development/Testing
```bash
Use: finops-minimal-policy.json
Why: Basic permissions for testing all tools
```

### Production (Single Account)
```bash
Use: finops-full-policy.json
Why: Complete access for all 24 tools
```

### Production (Multi-Account)
```bash
Use: finops-full-policy.json + finops-cross-account-role.json
Why: Centralized FinOps with cross-account access
```

### Cost Analysis Only
```bash
Use: finops-cost-only-policy.json
Why: Limited to cost analysis tools (9 tools)
```

### Maximum Security
```bash
Use: finops-readonly-policy.json
Why: Read-only access with no write permissions
```

---

## 🔧 Customization

### Add Custom Permissions

Edit any policy file and add your custom permissions:

```json
{
  "Sid": "CustomPermissions",
  "Effect": "Allow",
  "Action": [
    "your-service:YourAction"
  ],
  "Resource": "*"
}
```

### Restrict to Specific Regions

Add a condition to limit operations to specific regions:

```json
{
  "Condition": {
    "StringEquals": {
      "aws:RequestedRegion": [
        "us-east-1",
        "us-west-2"
      ]
    }
  }
}
```

### Restrict to Specific Resources

Limit access to resources with specific tags:

```json
{
  "Condition": {
    "StringEquals": {
      "aws:ResourceTag/Environment": "production"
    }
  }
}
```

---

## 🧪 Testing Permissions

### Test with AWS CLI

```bash
# Test EC2 permissions
aws ec2 describe-instances --region us-east-1

# Test Cost Explorer permissions
aws ce get-cost-and-usage \
  --time-period Start=2024-01-01,End=2024-01-31 \
  --granularity MONTHLY \
  --metrics UnblendedCost

# Test Cost Optimization Hub permissions
aws cost-optimization-hub list-recommendations
```

### Test with IAM Policy Simulator

```bash
aws iam simulate-principal-policy \
  --policy-source-arn arn:aws:iam::ACCOUNT_ID:user/finops-user \
  --action-names ec2:DescribeInstances \
  --resource-arns "*"
```

---

## 📝 Policy Validation

### Validate JSON Syntax

```bash
# Using jq
jq empty iam-policies/finops-full-policy.json

# Using Python
python -m json.tool iam-policies/finops-full-policy.json
```

### Validate with AWS

```bash
aws iam validate-policy \
  --policy-document file://iam-policies/finops-full-policy.json
```

---

## 🚨 Troubleshooting

### Common Issues

**Issue**: Access Denied errors
```bash
Solution: Check CloudTrail logs for denied API calls
aws cloudtrail lookup-events --lookup-attributes AttributeKey=EventName,AttributeValue=DescribeInstances
```

**Issue**: Cost Explorer not working
```bash
Solution: Ensure Cost Explorer is enabled in billing console
aws ce get-cost-and-usage --time-period Start=2024-01-01,End=2024-01-31 --granularity MONTHLY --metrics UnblendedCost
```

**Issue**: Cross-account role assumption fails
```bash
Solution: Verify trust policy and external ID
aws sts assume-role --role-arn arn:aws:iam::ACCOUNT_ID:role/finops-role --role-session-name test
```

---

## 📚 Additional Resources

- [AWS IAM Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)
- [AWS Cost Explorer API](https://docs.aws.amazon.com/cost-management/latest/APIReference/API_Operations_AWS_Cost_Explorer_Service.html)
- [AWS Cost Optimization Hub](https://docs.aws.amazon.com/cost-optimization-hub/latest/userguide/what-is.html)
- [IAM Policy Simulator](https://policysim.aws.amazon.com/)

---

## 🔄 Policy Updates

### Version History

- **v1.0** (2026-01-22) - Initial release with 5 policy templates
  - Full policy
  - Minimal policy
  - Read-only policy
  - Cost-only policy
  - Cross-account role trust policy

### Updating Policies

```bash
# Update existing policy
aws iam create-policy-version \
  --policy-arn arn:aws:iam::ACCOUNT_ID:policy/FinOpsFullPolicy \
  --policy-document file://iam-policies/finops-full-policy.json \
  --set-as-default
```

---

## 📞 Support

For issues or questions about IAM policies:
1. Check AWS CloudTrail for denied API calls
2. Use IAM Policy Simulator to test permissions
3. Review AWS documentation for specific services
4. Consult with your security team

---

**Last Updated**: January 22, 2026  
**Version**: 1.0  
**Policies**: 5
