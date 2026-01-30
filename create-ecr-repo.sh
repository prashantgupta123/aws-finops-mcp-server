#!/bin/bash

# Create ECR repository for AgentCore deployment
set -e

echo "🔧 Creating ECR repository for AWS FinOps MCP Server..."

REPO_NAME="aws-finops-mcp-server"
AWS_REGION="${AWS_REGION:-us-east-1}"

# Check if repository already exists
if aws ecr describe-repositories --repository-names "$REPO_NAME" --region "$AWS_REGION" &>/dev/null; then
    echo "✅ ECR repository '$REPO_NAME' already exists"
    REPO_URI=$(aws ecr describe-repositories --repository-names "$REPO_NAME" --region "$AWS_REGION" --query 'repositories[0].repositoryUri' --output text)
else
    echo "📦 Creating ECR repository '$REPO_NAME'..."
    REPO_URI=$(aws ecr create-repository \
        --repository-name "$REPO_NAME" \
        --region "$AWS_REGION" \
        --image-scanning-configuration scanOnPush=true \
        --encryption-configuration encryptionType=AES256 \
        --query 'repository.repositoryUri' \
        --output text)
    echo "✅ ECR repository created: $REPO_URI"
fi

echo ""
echo "📋 Repository Details:"
echo "   Name: $REPO_NAME"
echo "   URI: $REPO_URI"
echo "   Region: $AWS_REGION"
echo ""
echo "✅ ECR repository is ready for AgentCore deployment!"
