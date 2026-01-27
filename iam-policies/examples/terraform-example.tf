# Terraform configuration for AWS FinOps MCP Server IAM resources

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# Variables
variable "role_name" {
  description = "Name of the IAM role"
  type        = string
  default     = "finops-mcp-role"
}

variable "policy_type" {
  description = "Type of policy to use (full, minimal, readonly, cost-only)"
  type        = string
  default     = "full"
  validation {
    condition     = contains(["full", "minimal", "readonly", "cost-only"], var.policy_type)
    error_message = "Policy type must be one of: full, minimal, readonly, cost-only"
  }
}

variable "deployment_type" {
  description = "Deployment type (ec2, ecs, lambda)"
  type        = string
  default     = "ec2"
  validation {
    condition     = contains(["ec2", "ecs", "lambda"], var.deployment_type)
    error_message = "Deployment type must be one of: ec2, ecs, lambda"
  }
}

# Data source for current AWS account
data "aws_caller_identity" "current" {}

# Trust policy based on deployment type
data "aws_iam_policy_document" "trust_policy" {
  statement {
    effect = "Allow"
    principals {
      type = "Service"
      identifiers = [
        var.deployment_type == "ec2" ? "ec2.amazonaws.com" :
        var.deployment_type == "ecs" ? "ecs-tasks.amazonaws.com" :
        "lambda.amazonaws.com"
      ]
    }
    actions = ["sts:AssumeRole"]
  }
}

# IAM Role
resource "aws_iam_role" "finops_role" {
  name               = var.role_name
  assume_role_policy = data.aws_iam_policy_document.trust_policy.json
  description        = "IAM role for AWS FinOps MCP Server"

  tags = {
    Application = "FinOpsMCP"
    ManagedBy   = "Terraform"
    Environment = terraform.workspace
  }
}

# IAM Policy
resource "aws_iam_policy" "finops_policy" {
  name        = "${var.role_name}-policy"
  description = "Permissions for AWS FinOps MCP Server (${var.policy_type})"
  policy      = file("${path.module}/../finops-${var.policy_type}-policy.json")

  tags = {
    Application = "FinOpsMCP"
    ManagedBy   = "Terraform"
    PolicyType  = var.policy_type
  }
}

# Attach policy to role
resource "aws_iam_role_policy_attachment" "finops_attach" {
  role       = aws_iam_role.finops_role.name
  policy_arn = aws_iam_policy.finops_policy.arn
}

# Instance profile (for EC2 deployment)
resource "aws_iam_instance_profile" "finops_profile" {
  count = var.deployment_type == "ec2" ? 1 : 0
  name  = "${var.role_name}-profile"
  role  = aws_iam_role.finops_role.name

  tags = {
    Application = "FinOpsMCP"
    ManagedBy   = "Terraform"
  }
}

# Outputs
output "role_arn" {
  description = "ARN of the IAM role"
  value       = aws_iam_role.finops_role.arn
}

output "role_name" {
  description = "Name of the IAM role"
  value       = aws_iam_role.finops_role.name
}

output "policy_arn" {
  description = "ARN of the IAM policy"
  value       = aws_iam_policy.finops_policy.arn
}

output "instance_profile_arn" {
  description = "ARN of the instance profile (EC2 only)"
  value       = var.deployment_type == "ec2" ? aws_iam_instance_profile.finops_profile[0].arn : null
}

output "usage_instructions" {
  description = "Instructions for using the created resources"
  value = var.deployment_type == "ec2" ? (
    "Attach instance profile to EC2: aws ec2 associate-iam-instance-profile --instance-id i-xxxxx --iam-instance-profile Name=${aws_iam_instance_profile.finops_profile[0].name}"
  ) : var.deployment_type == "ecs" ? (
    "Use in ECS task definition: \"taskRoleArn\": \"${aws_iam_role.finops_role.arn}\""
  ) : (
    "Use in Lambda function: aws lambda update-function-configuration --function-name finops-mcp --role ${aws_iam_role.finops_role.arn}"
  )
}

# Example usage:
# terraform init
# terraform plan -var="policy_type=full" -var="deployment_type=ec2"
# terraform apply -var="policy_type=full" -var="deployment_type=ec2"
