# IAM Setup Guide - AWS FinOps MCP Server

Complete guide for setting up IAM permissions for your AWS FinOps MCP Server.

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Policy Types](#policy-types)
3. [Deployment Scenarios](#deployment-scenarios)
4. [Setup Methods](#setup-methods)
5. [Security Best Practices](#security-best-practices)
6. [Troubleshooting](#troubleshooting)

---

## 🚀 Quick Start

### Option 1: Automated Script (Recommended)

```bash
# For EC2 deployment with full permissions
cd iam-policies/examples
./create-iam-role.sh finops-mcp-role full ec2

# For IAM user with minimal permissions
./create-iam-user.sh finops-mcp-user minimal
```

### Option 2: AWS Console

1. Go to **IAM Console** → **Policies** → **Create Policy**
2. Select **JSON** tab
3. Copy content from `iam-policies/finops-full-policy.json`
4. Click **Review policy** → Name it `FinOpsFullPolicy`
5. Go to **Roles** → **Create Role**
6. Select **EC2** (or your service)
7. Attach `FinOpsFullPolicy`
8. Name it `finops-mcp-role`

### Option 3: AWS CLI

```bash
# Create policy
aws iam create-policy \
  --policy-name FinOpsFullPolicy \
  --policy-document file://iam-policies/finops-full-policy.json

# Create role
aws iam create-role \
  --role-name finops-mcp-role \
  --assume-role-policy-document file://iam-policies/trust-policies/ec2-trust-policy.json

# Attach policy
aws iam attach-role-policy \
  --role-name finops-mcp-role \
  --policy-arn arn:aws:iam::ACCOUNT_ID:policy/FinOpsFullPolicy
```

---

## 📊 Policy Types

### 1. Full Policy (Recommended for Production)

**File**: `iam-policies/finops-full-policy.json`

**Features**:
- ✅ All 24 tools enabled
- ✅ Granular permissions (no wildcards)
- ✅ Read-only access
- ✅ Cost Explorer + Cost Optimization Hub
- ✅ CloudWatch metrics

**Use When**:
- Running in production
- Need all FinOps capabilities
- Want detailed resource analysis

**Tools Enabled**: All 24 tools

---

### 2. Minimal Policy

**File**: `iam-policies/finops-minimal-policy.json`

**Features**:
- ✅ Basic describe/list permissions
- ✅ Smaller policy size
- ✅ Quick setup for testing

**Use When**:
- Testing the MCP server
- Limited scope deployment
- Want to add permissions incrementally

**Tools Enabled**: All 24 tools (with basic permissions)

---

### 3. Read-Only Policy

**File**: `iam-policies/finops-readonly-policy.json`

**Features**:
- ✅ Maximum security
- ✅ All Describe*, Get*, List* actions
- ✅ No write permissions possible

**Use When**:
- Security is paramount
- Compliance requirements
- Audit-only access needed

**Tools Enabled**: All 24 tools

---

### 4. Cost-Only Policy

**File**: `iam-policies/finops-cost-only-policy.json`

**Features**:
- ✅ Cost Explorer only
- ✅ Cost Optimization Hub only
- ✅ Minimal permissions

**Use When**:
- Only need cost analysis
- Finance team access
- Budget monitoring

**Tools Enabled**: 9 tools (Cost Explorer + Cost Optimization)

---

## 🎯 Deployment Scenarios

### Scenario 1: EC2 Instance

**Setup**:
```bash
# Create role with instance profile
./iam-policies/examples/create-iam-role.sh finops-mcp-role full ec2

# Create instance profile
aws iam create-instance-profile --instance-profile-name finops-mcp-profile

# Add role to profile
aws iam add-role-to-instance-profile \
  --instance-profile-name finops-mcp-profile \
  --role-name finops-mcp-role

# Attach to EC2 instance
aws ec2 associate-iam-instance-profile \
  --instance-id i-xxxxx \
  --iam-instance-profile Name=finops-mcp-profile
```

**MCP Config**:
```json
{
  "mcpServers": {
    "aws-finops": {
      "command": "python",
      "args": ["-m", "aws_finops_mcp"],
      "env": {
        "AWS_REGION": "us-east-1"
      }
    }
  }
}
```

---

### Scenario 2: ECS Fargate

**Setup**:
```bash
# Create role
./iam-policies/examples/create-iam-role.sh finops-mcp-role full ecs
```

**Task Definition**:
```json
{
  "family": "finops-mcp",
  "taskRoleArn": "arn:aws:iam::ACCOUNT_ID:role/finops-mcp-role",
  "executionRoleArn": "arn:aws:iam::ACCOUNT_ID:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "finops-mcp",
      "image": "your-registry/finops-mcp:latest",
      "memory": 512,
      "cpu": 256
    }
  ]
}
```

---

### Scenario 3: Lambda Function

**Setup**:
```bash
# Create role
./iam-policies/examples/create-iam-role.sh finops-mcp-role full lambda

# Update Lambda function
aws lambda update-function-configuration \
  --function-name finops-mcp \
  --role arn:aws:iam::ACCOUNT_ID:role/finops-mcp-role
```

---

### Scenario 4: Local Development

**Setup**:
```bash
# Create IAM user
./iam-policies/examples/create-iam-user.sh finops-mcp-user full

# Configure AWS CLI
aws configure --profile finops
```

**MCP Config**:
```json
{
  "mcpServers": {
    "aws-finops": {
      "command": "python",
      "args": ["-m", "aws_finops_mcp"],
      "env": {
        "AWS_PROFILE": "finops",
        "AWS_REGION": "us-east-1"
      }
    }
  }
}
```

---

### Scenario 5: Multi-Account (Cross-Account)

**Setup in Target Account**:
```bash
# Create role with cross-account trust
aws iam create-role \
  --role-name finops-mcp-role \
  --assume-role-policy-document file://iam-policies/finops-cross-account-role.json

# Attach permissions
aws iam attach-role-policy \
  --role-name finops-mcp-role \
  --policy-arn arn:aws:iam::ACCOUNT_ID:policy/FinOpsFullPolicy
```

**Edit Trust Policy**:
Replace in `finops-cross-account-role.json`:
- `MANAGEMENT_ACCOUNT_ID` → Your management account ID
- `finops-mcp-server-unique-id` → Your unique external ID

**MCP Config**:
```json
{
  "tool": "find_unused_lambda_functions",
  "arguments": {
    "role_arn": "arn:aws:iam::TARGET_ACCOUNT:role/finops-mcp-role",
    "region_name": "us-east-1"
  }
}
```

---

## 🛠️ Setup Methods

### Method 1: Bash Scripts

**Create IAM Role**:
```bash
cd iam-policies/examples
./create-iam-role.sh [role-name] [policy-type] [deployment-type]

# Examples:
./create-iam-role.sh finops-mcp-role full ec2
./create-iam-role.sh finops-ecs-role minimal ecs
./create-iam-role.sh finops-lambda-role readonly lambda
```

**Create IAM User**:
```bash
./create-iam-user.sh [user-name] [policy-type]

# Examples:
./create-iam-user.sh finops-mcp-user full
./create-iam-user.sh finops-dev-user minimal
```

---

### Method 2: Terraform

```bash
cd iam-policies/examples

# Initialize
terraform init

# Plan
terraform plan \
  -var="role_name=finops-mcp-role" \
  -var="policy_type=full" \
  -var="deployment_type=ec2"

# Apply
terraform apply \
  -var="role_name=finops-mcp-role" \
  -var="policy_type=full" \
  -var="deployment_type=ec2"
```

---

### Method 3: CloudFormation

```bash
aws cloudformation create-stack \
  --stack-name finops-mcp-iam \
  --template-body file://iam-policies/examples/cloudformation-example.yaml \
  --parameters \
    ParameterKey=RoleName,ParameterValue=finops-mcp-role \
    ParameterKey=PolicyType,ParameterValue=full \
    ParameterKey=DeploymentType,ParameterValue=ec2 \
  --capabilities CAPABILITY_NAMED_IAM
```

---

## 🔒 Security Best Practices

### 1. Use IAM Roles (Not Users)

**Why**: Temporary credentials, automatic rotation, no key management

**How**:
```bash
# For EC2/ECS/Lambda
./create-iam-role.sh finops-mcp-role full ec2
```

---

### 2. Enable CloudTrail

**Monitor all API calls**:
```bash
aws cloudtrail create-trail \
  --name finops-audit-trail \
  --s3-bucket-name finops-audit-logs

aws cloudtrail start-logging --name finops-audit-trail
```

---

### 3. Use External ID for Cross-Account

**Prevent confused deputy problem**:
```json
{
  "Condition": {
    "StringEquals": {
      "sts:ExternalId": "your-unique-external-id-12345"
    }
  }
}
```

---

### 4. Restrict to Specific Regions

**Add condition to policy**:
```json
{
  "Condition": {
    "StringEquals": {
      "aws:RequestedRegion": ["us-east-1", "us-west-2"]
    }
  }
}
```

---

### 5. Use Resource Tags

**Limit to tagged resources**:
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

### 6. Rotate Credentials

**For IAM users**:
```bash
# Create new key
aws iam create-access-key --user-name finops-mcp-user

# Delete old key (after testing)
aws iam delete-access-key \
  --user-name finops-mcp-user \
  --access-key-id AKIA...
```

---

### 7. Use AWS Secrets Manager

**Store credentials securely**:
```bash
aws secretsmanager create-secret \
  --name finops-mcp-credentials \
  --secret-string '{"access_key":"AKIA...","secret_key":"..."}'
```

---

## 🧪 Testing Permissions

### Test EC2 Permissions

```bash
aws ec2 describe-instances --region us-east-1
```

### Test Cost Explorer Permissions

```bash
aws ce get-cost-and-usage \
  --time-period Start=2024-01-01,End=2024-01-31 \
  --granularity MONTHLY \
  --metrics UnblendedCost
```

### Test Cost Optimization Hub

```bash
aws cost-optimization-hub list-recommendations
```

### Test with IAM Policy Simulator

```bash
aws iam simulate-principal-policy \
  --policy-source-arn arn:aws:iam::ACCOUNT_ID:role/finops-mcp-role \
  --action-names ec2:DescribeInstances ce:GetCostAndUsage \
  --resource-arns "*"
```

---

## 🚨 Troubleshooting

### Issue: Access Denied

**Check CloudTrail**:
```bash
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=EventName,AttributeValue=DescribeInstances \
  --max-results 10
```

**Solution**: Add missing permission to policy

---

### Issue: Cost Explorer Not Working

**Check if enabled**:
```bash
aws ce get-cost-and-usage \
  --time-period Start=2024-01-01,End=2024-01-31 \
  --granularity MONTHLY \
  --metrics UnblendedCost
```

**Solution**: Enable Cost Explorer in AWS Billing Console

---

### Issue: Cross-Account Role Assumption Fails

**Test assumption**:
```bash
aws sts assume-role \
  --role-arn arn:aws:iam::TARGET_ACCOUNT:role/finops-mcp-role \
  --role-session-name test \
  --external-id your-external-id
```

**Solution**: Check trust policy and external ID

---

### Issue: Instance Profile Not Found

**List profiles**:
```bash
aws iam list-instance-profiles
```

**Solution**: Create instance profile and add role

---

## 📚 Additional Resources

- [AWS IAM Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)
- [AWS Cost Explorer API](https://docs.aws.amazon.com/cost-management/latest/APIReference/API_Operations_AWS_Cost_Explorer_Service.html)
- [AWS Cost Optimization Hub](https://docs.aws.amazon.com/cost-optimization-hub/latest/userguide/what-is.html)
- [IAM Policy Simulator](https://policysim.aws.amazon.com/)

---

## 📞 Support

For issues with IAM setup:
1. Check CloudTrail for denied API calls
2. Use IAM Policy Simulator
3. Review AWS documentation
4. Consult security team

---

**Last Updated**: January 22, 2026  
**Version**: 1.0
