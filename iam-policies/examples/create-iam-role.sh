#!/bin/bash
# Script to create IAM role for AWS FinOps MCP Server

set -e

# Configuration
ROLE_NAME="${1:-finops-mcp-role}"
POLICY_TYPE="${2:-full}"  # full, minimal, readonly, cost-only
DEPLOYMENT_TYPE="${3:-ec2}"  # ec2, ecs, lambda, user

echo "=========================================="
echo "AWS FinOps MCP Server - IAM Role Setup"
echo "=========================================="
echo "Role Name: $ROLE_NAME"
echo "Policy Type: $POLICY_TYPE"
echo "Deployment Type: $DEPLOYMENT_TYPE"
echo ""

# Get AWS account ID
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo "AWS Account ID: $ACCOUNT_ID"
echo ""

# Select trust policy based on deployment type
case $DEPLOYMENT_TYPE in
  ec2)
    TRUST_POLICY="trust-policies/ec2-trust-policy.json"
    ;;
  ecs)
    TRUST_POLICY="trust-policies/ecs-trust-policy.json"
    ;;
  lambda)
    TRUST_POLICY="trust-policies/lambda-trust-policy.json"
    ;;
  user)
    echo "For user deployment, create a user instead:"
    echo "aws iam create-user --user-name finops-mcp-user"
    exit 0
    ;;
  *)
    echo "Invalid deployment type: $DEPLOYMENT_TYPE"
    echo "Valid options: ec2, ecs, lambda, user"
    exit 1
    ;;
esac

# Select permission policy
case $POLICY_TYPE in
  full)
    POLICY_FILE="finops-full-policy.json"
    POLICY_NAME="FinOpsFullPolicy"
    ;;
  minimal)
    POLICY_FILE="finops-minimal-policy.json"
    POLICY_NAME="FinOpsMinimalPolicy"
    ;;
  readonly)
    POLICY_FILE="finops-readonly-policy.json"
    POLICY_NAME="FinOpsReadOnlyPolicy"
    ;;
  cost-only)
    POLICY_FILE="finops-cost-only-policy.json"
    POLICY_NAME="FinOpsCostOnlyPolicy"
    ;;
  *)
    echo "Invalid policy type: $POLICY_TYPE"
    echo "Valid options: full, minimal, readonly, cost-only"
    exit 1
    ;;
esac

echo "Step 1: Creating IAM role..."
aws iam create-role \
  --role-name "$ROLE_NAME" \
  --assume-role-policy-document "file://$TRUST_POLICY" \
  --description "IAM role for AWS FinOps MCP Server" \
  --tags Key=Application,Value=FinOpsMCP Key=ManagedBy,Value=Script

echo "✅ Role created: $ROLE_NAME"
echo ""

echo "Step 2: Creating IAM policy..."
POLICY_ARN=$(aws iam create-policy \
  --policy-name "$POLICY_NAME" \
  --policy-document "file://$POLICY_FILE" \
  --description "Permissions for AWS FinOps MCP Server ($POLICY_TYPE)" \
  --tags Key=Application,Value=FinOpsMCP Key=ManagedBy,Value=Script \
  --query 'Policy.Arn' \
  --output text 2>/dev/null || echo "arn:aws:iam::$ACCOUNT_ID:policy/$POLICY_NAME")

echo "✅ Policy created/found: $POLICY_ARN"
echo ""

echo "Step 3: Attaching policy to role..."
aws iam attach-role-policy \
  --role-name "$ROLE_NAME" \
  --policy-arn "$POLICY_ARN"

echo "✅ Policy attached to role"
echo ""

echo "=========================================="
echo "✅ Setup Complete!"
echo "=========================================="
echo ""
echo "Role ARN: arn:aws:iam::$ACCOUNT_ID:role/$ROLE_NAME"
echo "Policy ARN: $POLICY_ARN"
echo ""

# Deployment-specific instructions
case $DEPLOYMENT_TYPE in
  ec2)
    echo "Next Steps for EC2:"
    echo "1. Create instance profile:"
    echo "   aws iam create-instance-profile --instance-profile-name $ROLE_NAME-profile"
    echo ""
    echo "2. Add role to instance profile:"
    echo "   aws iam add-role-to-instance-profile --instance-profile-name $ROLE_NAME-profile --role-name $ROLE_NAME"
    echo ""
    echo "3. Attach to EC2 instance:"
    echo "   aws ec2 associate-iam-instance-profile --instance-id i-xxxxx --iam-instance-profile Name=$ROLE_NAME-profile"
    ;;
  ecs)
    echo "Next Steps for ECS:"
    echo "1. Update task definition with taskRoleArn:"
    echo "   \"taskRoleArn\": \"arn:aws:iam::$ACCOUNT_ID:role/$ROLE_NAME\""
    echo ""
    echo "2. Register new task definition revision"
    echo ""
    echo "3. Update ECS service with new task definition"
    ;;
  lambda)
    echo "Next Steps for Lambda:"
    echo "1. Create Lambda function with role:"
    echo "   aws lambda create-function --role arn:aws:iam::$ACCOUNT_ID:role/$ROLE_NAME ..."
    echo ""
    echo "2. Or update existing function:"
    echo "   aws lambda update-function-configuration --function-name finops-mcp --role arn:aws:iam::$ACCOUNT_ID:role/$ROLE_NAME"
    ;;
esac

echo ""
echo "To use with MCP server, set environment variable:"
echo "export AWS_ROLE_ARN=arn:aws:iam::$ACCOUNT_ID:role/$ROLE_NAME"
