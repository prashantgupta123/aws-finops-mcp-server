#!/bin/bash
# AMI Update Helper Scripts for Auto Scaling Groups
# Region: ap-south-1
# Generated: January 22, 2026

set -e

REGION="ap-south-1"
COLOR_GREEN='\033[0;32m'
COLOR_YELLOW='\033[1;33m'
COLOR_RED='\033[0;31m'
COLOR_RESET='\033[0m'

# Function to print colored output
print_info() {
    echo -e "${COLOR_GREEN}[INFO]${COLOR_RESET} $1"
}

print_warning() {
    echo -e "${COLOR_YELLOW}[WARNING]${COLOR_RESET} $1"
}

print_error() {
    echo -e "${COLOR_RED}[ERROR]${COLOR_RESET} $1"
}

# ============================================================================
# 1. Find Latest AMI
# ============================================================================

find_latest_ecs_ami() {
    local arch=$1  # x86_64 or arm64
    
    print_info "Finding latest ECS-optimized Amazon Linux 2023 AMI for ${arch}..."
    
    if [ "$arch" == "arm64" ]; then
        aws ssm get-parameter \
            --name /aws/service/ecs/optimized-ami/amazon-linux-2023/arm64/recommended \
            --region $REGION \
            --query 'Parameter.Value' \
            --output text | jq -r '.image_id, .image_name'
    else
        aws ssm get-parameter \
            --name /aws/service/ecs/optimized-ami/amazon-linux-2023/recommended \
            --region $REGION \
            --query 'Parameter.Value' \
            --output text | jq -r '.image_id, .image_name'
    fi
}

find_latest_eks_ami() {
    local k8s_version=$1  # e.g., 1.32
    local arch=$2         # x86_64 or arm64
    
    print_info "Finding latest EKS-optimized AMI for Kubernetes ${k8s_version} (${arch})..."
    
    aws ssm get-parameter \
        --name "/aws/service/eks/optimized-ami/${k8s_version}/amazon-linux-2023/${arch}/recommended" \
        --region $REGION \
        --query 'Parameter.Value' \
        --output text | jq -r '.image_id, .image_name'
}

# ============================================================================
# 2. Get ASG Current Configuration
# ============================================================================

get_asg_info() {
    local asg_name=$1
    
    print_info "Getting information for ASG: ${asg_name}"
    
    aws autoscaling describe-auto-scaling-groups \
        --auto-scaling-group-names "$asg_name" \
        --region $REGION \
        --query 'AutoScalingGroups[0].[AutoScalingGroupName,MinSize,MaxSize,DesiredCapacity,LaunchTemplate.LaunchTemplateId,LaunchTemplate.Version]' \
        --output table
}

get_current_ami() {
    local asg_name=$1
    
    print_info "Getting current AMI for ASG: ${asg_name}"
    
    # Get launch template ID
    local lt_id=$(aws autoscaling describe-auto-scaling-groups \
        --auto-scaling-group-names "$asg_name" \
        --region $REGION \
        --query 'AutoScalingGroups[0].LaunchTemplate.LaunchTemplateId' \
        --output text)
    
    if [ "$lt_id" == "None" ] || [ -z "$lt_id" ]; then
        print_error "No launch template found for ASG: ${asg_name}"
        return 1
    fi
    
    # Get AMI from launch template
    aws ec2 describe-launch-template-versions \
        --launch-template-id "$lt_id" \
        --versions '$Latest' \
        --region $REGION \
        --query 'LaunchTemplateVersions[0].[LaunchTemplateId,VersionNumber,LaunchTemplateData.ImageId]' \
        --output table
    
    # Get AMI details
    local ami_id=$(aws ec2 describe-launch-template-versions \
        --launch-template-id "$lt_id" \
        --versions '$Latest' \
        --region $REGION \
        --query 'LaunchTemplateVersions[0].LaunchTemplateData.ImageId' \
        --output text)
    
    aws ec2 describe-images \
        --image-ids "$ami_id" \
        --region $REGION \
        --query 'Images[0].[ImageId,Name,CreationDate,Architecture]' \
        --output table
}

# ============================================================================
# 3. Update Launch Template
# ============================================================================

update_launch_template() {
    local asg_name=$1
    local new_ami_id=$2
    
    print_info "Updating launch template for ASG: ${asg_name}"
    
    # Get launch template ID
    local lt_id=$(aws autoscaling describe-auto-scaling-groups \
        --auto-scaling-group-names "$asg_name" \
        --region $REGION \
        --query 'AutoScalingGroups[0].LaunchTemplate.LaunchTemplateId' \
        --output text)
    
    if [ "$lt_id" == "None" ] || [ -z "$lt_id" ]; then
        print_error "No launch template found for ASG: ${asg_name}"
        return 1
    fi
    
    print_info "Launch Template ID: ${lt_id}"
    print_info "New AMI ID: ${new_ami_id}"
    
    # Create new version
    print_info "Creating new launch template version..."
    aws ec2 create-launch-template-version \
        --launch-template-id "$lt_id" \
        --source-version '$Latest' \
        --launch-template-data "{\"ImageId\":\"${new_ami_id}\"}" \
        --region $REGION
    
    # Set as default
    print_info "Setting new version as default..."
    aws ec2 modify-launch-template \
        --launch-template-id "$lt_id" \
        --default-version '$Latest' \
        --region $REGION
    
    print_info "Launch template updated successfully!"
}

# ============================================================================
# 4. Start Instance Refresh
# ============================================================================

start_instance_refresh() {
    local asg_name=$1
    local min_healthy_pct=${2:-90}
    local warmup=${3:-300}
    
    print_info "Starting instance refresh for ASG: ${asg_name}"
    print_warning "Min Healthy Percentage: ${min_healthy_pct}%"
    print_warning "Instance Warmup: ${warmup} seconds"
    
    aws autoscaling start-instance-refresh \
        --auto-scaling-group-name "$asg_name" \
        --preferences "{
            \"MinHealthyPercentage\": ${min_healthy_pct},
            \"InstanceWarmup\": ${warmup},
            \"CheckpointPercentages\": [50, 100],
            \"CheckpointDelay\": 300
        }" \
        --region $REGION
    
    print_info "Instance refresh started! Monitor with: check_refresh_status ${asg_name}"
}

# ============================================================================
# 5. Monitor Instance Refresh
# ============================================================================

check_refresh_status() {
    local asg_name=$1
    
    print_info "Checking instance refresh status for ASG: ${asg_name}"
    
    aws autoscaling describe-instance-refreshes \
        --auto-scaling-group-name "$asg_name" \
        --region $REGION \
        --query 'InstanceRefreshes[0].[Status,StatusReason,PercentageComplete,InstancesToUpdate]' \
        --output table
}

watch_refresh_status() {
    local asg_name=$1
    local interval=${2:-30}
    
    print_info "Watching instance refresh for ASG: ${asg_name} (checking every ${interval}s)"
    print_warning "Press Ctrl+C to stop watching"
    
    while true; do
        clear
        echo "=== Instance Refresh Status for ${asg_name} ==="
        echo "Time: $(date)"
        echo ""
        
        check_refresh_status "$asg_name"
        
        local status=$(aws autoscaling describe-instance-refreshes \
            --auto-scaling-group-name "$asg_name" \
            --region $REGION \
            --query 'InstanceRefreshes[0].Status' \
            --output text)
        
        if [ "$status" == "Successful" ]; then
            print_info "Instance refresh completed successfully!"
            break
        elif [ "$status" == "Failed" ] || [ "$status" == "Cancelled" ]; then
            print_error "Instance refresh ${status}!"
            break
        fi
        
        sleep $interval
    done
}

# ============================================================================
# 6. Cancel Instance Refresh (Rollback)
# ============================================================================

cancel_instance_refresh() {
    local asg_name=$1
    
    print_warning "Cancelling instance refresh for ASG: ${asg_name}"
    
    aws autoscaling cancel-instance-refresh \
        --auto-scaling-group-name "$asg_name" \
        --region $REGION
    
    print_info "Instance refresh cancelled!"
}

# ============================================================================
# 7. Rollback Launch Template
# ============================================================================

rollback_launch_template() {
    local asg_name=$1
    local version=${2:-'$Latest-1'}
    
    print_warning "Rolling back launch template for ASG: ${asg_name}"
    
    # Get launch template ID
    local lt_id=$(aws autoscaling describe-auto-scaling-groups \
        --auto-scaling-group-names "$asg_name" \
        --region $REGION \
        --query 'AutoScalingGroups[0].LaunchTemplate.LaunchTemplateId' \
        --output text)
    
    if [ "$version" == '$Latest-1' ]; then
        # Get current version number and subtract 1
        local current_version=$(aws ec2 describe-launch-template-versions \
            --launch-template-id "$lt_id" \
            --versions '$Latest' \
            --region $REGION \
            --query 'LaunchTemplateVersions[0].VersionNumber' \
            --output text)
        
        version=$((current_version - 1))
    fi
    
    print_info "Rolling back to version: ${version}"
    
    aws ec2 modify-launch-template \
        --launch-template-id "$lt_id" \
        --default-version "$version" \
        --region $REGION
    
    print_info "Launch template rolled back to version ${version}"
}

# ============================================================================
# 8. Batch Update for Phase 1 (Scaled-to-Zero ASGs)
# ============================================================================

update_phase1_asgs() {
    local new_ami_id=$1
    
    if [ -z "$new_ami_id" ]; then
        print_error "Please provide new AMI ID"
        echo "Usage: update_phase1_asgs <AMI_ID>"
        return 1
    fi
    
    print_info "Starting Phase 1 updates (scaled-to-zero ASGs)"
    print_info "New AMI: ${new_ami_id}"
    
    local asgs=(
        "live-bootcamp"
        "live-desk-allocation"
        "live-newi"
        "live-v1-growth"
    )
    
    for asg in "${asgs[@]}"; do
        print_info "Processing ASG: ${asg}"
        update_launch_template "$asg" "$new_ami_id"
        echo ""
    done
    
    print_info "Phase 1 updates completed!"
}

# ============================================================================
# 9. Full Update Workflow
# ============================================================================

full_update_workflow() {
    local asg_name=$1
    local new_ami_id=$2
    
    if [ -z "$asg_name" ] || [ -z "$new_ami_id" ]; then
        print_error "Missing required parameters"
        echo "Usage: full_update_workflow <ASG_NAME> <NEW_AMI_ID>"
        return 1
    fi
    
    print_info "=== Full Update Workflow for ${asg_name} ==="
    echo ""
    
    # Step 1: Show current config
    print_info "Step 1: Current Configuration"
    get_asg_info "$asg_name"
    get_current_ami "$asg_name"
    echo ""
    
    # Step 2: Confirm
    read -p "Continue with update? (yes/no): " confirm
    if [ "$confirm" != "yes" ]; then
        print_warning "Update cancelled"
        return 0
    fi
    
    # Step 3: Update launch template
    print_info "Step 2: Updating Launch Template"
    update_launch_template "$asg_name" "$new_ami_id"
    echo ""
    
    # Step 4: Start instance refresh
    print_info "Step 3: Starting Instance Refresh"
    start_instance_refresh "$asg_name"
    echo ""
    
    # Step 5: Watch progress
    print_info "Step 4: Monitoring Progress"
    watch_refresh_status "$asg_name"
}

# ============================================================================
# 10. List All ASGs with AMI Info
# ============================================================================

list_all_asgs_with_ami() {
    print_info "Listing all ASGs with AMI information..."
    
    local asgs=$(aws autoscaling describe-auto-scaling-groups \
        --region $REGION \
        --query 'AutoScalingGroups[*].AutoScalingGroupName' \
        --output text)
    
    echo "ASG_NAME | AMI_ID | AMI_NAME | AMI_AGE"
    echo "---------|--------|----------|--------"
    
    for asg in $asgs; do
        local lt_id=$(aws autoscaling describe-auto-scaling-groups \
            --auto-scaling-group-names "$asg" \
            --region $REGION \
            --query 'AutoScalingGroups[0].LaunchTemplate.LaunchTemplateId' \
            --output text 2>/dev/null)
        
        if [ "$lt_id" != "None" ] && [ -n "$lt_id" ]; then
            local ami_id=$(aws ec2 describe-launch-template-versions \
                --launch-template-id "$lt_id" \
                --versions '$Latest' \
                --region $REGION \
                --query 'LaunchTemplateVersions[0].LaunchTemplateData.ImageId' \
                --output text 2>/dev/null)
            
            if [ -n "$ami_id" ] && [ "$ami_id" != "None" ]; then
                local ami_info=$(aws ec2 describe-images \
                    --image-ids "$ami_id" \
                    --region $REGION \
                    --query 'Images[0].[Name,CreationDate]' \
                    --output text 2>/dev/null)
                
                echo "${asg} | ${ami_id} | ${ami_info}"
            fi
        fi
    done
}

# ============================================================================
# Usage Examples
# ============================================================================

show_usage() {
    cat <<'EOF'
AMI Update Helper Scripts
=========================

Available Functions:

1. Find Latest AMIs:
   find_latest_ecs_ami arm64
   find_latest_ecs_ami x86_64
   find_latest_eks_ami 1.32 arm64

2. Get ASG Information:
   get_asg_info <ASG_NAME>
   get_current_ami <ASG_NAME>

3. Update Launch Template:
   update_launch_template <ASG_NAME> <NEW_AMI_ID>

4. Instance Refresh:
   start_instance_refresh <ASG_NAME> [MIN_HEALTHY_PCT] [WARMUP_SECONDS]
   check_refresh_status <ASG_NAME>
   watch_refresh_status <ASG_NAME> [INTERVAL_SECONDS]

5. Rollback:
   cancel_instance_refresh <ASG_NAME>
   rollback_launch_template <ASG_NAME> [VERSION]

6. Batch Operations:
   update_phase1_asgs <NEW_AMI_ID>
   list_all_asgs_with_ami

7. Full Workflow:
   full_update_workflow <ASG_NAME> <NEW_AMI_ID>

Examples:
---------
# Find latest ECS AMI for ARM64
find_latest_ecs_ami arm64

# Check current AMI for an ASG
get_current_ami live-ldap

# Update an ASG with new AMI
full_update_workflow live-ldap ami-0123456789abcdef0

# Batch update Phase 1 ASGs
update_phase1_asgs ami-0123456789abcdef0

# Monitor refresh progress
watch_refresh_status live-ldap 30

# Rollback if needed
cancel_instance_refresh live-ldap
rollback_launch_template live-ldap

EOF
}

# ============================================================================
# Main
# ============================================================================

# If script is executed (not sourced), show usage
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    show_usage
fi
