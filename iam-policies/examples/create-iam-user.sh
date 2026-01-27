#!/bin/bash
# Script to create IAM user for AWS FinOps MCP Server

set -e

# Configuration
USER_NAME="${1:-finops-mcp-user}"
POLICY_TYPE="${2:-full}"  # full, minimal, readonly, cost-only

echo "=========================================="
echo "AWS FinOps MCP Server - IAM User Setup"
echo "=========================================="
echo "User Name: $USER_NAME"
echo "Policy Type: $POLICY_TYPE"
echo ""

# Get AWS account ID
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo "AWS Account ID: $ACCOUNT_ID"
echo ""

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

echo "Step 1: Creating IAM user..."
aws iam create-user \
  --user-name "$USER_NAME" \
  --tags Key=Application,Value=FinOpsMCP Key=ManagedBy,Value=Script

echo "✅ User created: $USER_NAME"
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

echo "Step 3: Attaching policy to user..."
aws iam attach-user-policy \
  --user-name "$USER_NAME" \
  --policy-arn "$POLICY_ARN"

echo "✅ Policy attached to user"
echo ""

echo "Step 4: Creating access key..."
ACCESS_KEY_OUTPUT=$(aws iam create-access-key --user-name "$USER_NAME")
ACCESS_KEY_ID=$(echo "$ACCESS_KEY_OUTPUT" | jq -r '.AccessKey.AccessKeyId')
SECRET_ACCESS_KEY=$(echo "$ACCESS_KEY_OUTPUT" | jq -r '.AccessKey.SecretAccessKey')

echo "✅ Access key created"
echo ""

echo "=========================================="
echo "✅ Setup Complete!"
echo "=========================================="
echo ""
echo "User ARN: arn:aws:iam::$ACCOUNT_ID:user/$USER_NAME"
echo "Policy ARN: $POLICY_ARN"
echo ""
echo "⚠️  IMPORTANT: Save these credentials securely!"
echo "=========================================="
echo "Access Key ID: $ACCESS_KEY_ID"
echo "Secret Access Key: $SECRET_ACCESS_KEY"
echo "=========================================="
echo ""
echo "Next Steps:"
echo ""
echo "1. Configure AWS CLI profile:"
echo "   aws configure --profile finops"
echo "   AWS Access Key ID: $ACCESS_KEY_ID"
echo "   AWS Secret Access Key: $SECRET_ACCESS_KEY"
echo ""
echo "2. Or set environment variables:"
echo "   export AWS_ACCESS_KEY_ID=$ACCESS_KEY_ID"
echo "   export AWS_SECRET_ACCESS_KEY=$SECRET_ACCESS_KEY"
echo "   export AWS_REGION=us-east-1"
echo ""
echo "3. Or use in MCP server config:"
echo "   {\"access_key\": \"$ACCESS_KEY_ID\", \"secret_access_key\": \"$SECRET_ACCESS_KEY\"}"
echo ""
echo "⚠️  Store credentials in AWS Secrets Manager or secure vault!"
echo ""
echo "To store in Secrets Manager:"
echo "aws secretsmanager create-secret \\"
echo "  --name finops-mcp-credentials \\"
echo "  --secret-string '{\"access_key\":\"$ACCESS_KEY_ID\",\"secret_key\":\"$SECRET_ACCESS_KEY\"}'"
