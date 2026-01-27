# AWS FinOps MCP Server - Deployment Guide

This guide covers multiple deployment options for the AWS FinOps MCP Server.

## Table of Contents

1. [Local Development (Virtual Environment)](#local-development-virtual-environment)
2. [Docker Deployment](#docker-deployment)
3. [Production Deployment](#production-deployment)
4. [AWS Deployment Options](#aws-deployment-options)

---

## Local Development (Virtual Environment)

### Quick Start

```bash
# 1. Setup virtual environment and install
./setup.sh

# 2. Run the server
./run.sh

# 3. Run tests (optional)
./test.sh
```

### Manual Setup

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Linux/Mac
# or
venv\Scripts\activate     # On Windows

# Install package
pip install -e .

# Run server
python -m aws_finops_mcp

# Deactivate when done
deactivate
```

### Configuration

Set AWS credentials before running:

```bash
# Option 1: AWS Profile
export AWS_PROFILE=your-profile
export AWS_REGION=us-east-1

# Option 2: Access Keys
export AWS_ACCESS_KEY_ID=your-access-key
export AWS_SECRET_ACCESS_KEY=your-secret-key
export AWS_DEFAULT_REGION=us-east-1
```

---

## Docker Deployment

### Quick Start

```bash
# Build and run
./docker-run.sh run

# View logs
./docker-run.sh logs

# Stop
./docker-run.sh stop
```

### Docker Commands Reference

```bash
# Build image only
./docker-run.sh build

# Run container
./docker-run.sh run

# Start stopped container
./docker-run.sh start

# Stop container
./docker-run.sh stop

# Restart container
./docker-run.sh restart

# View logs
./docker-run.sh logs

# Open shell in container
./docker-run.sh shell

# Check status
./docker-run.sh status

# Clean up (remove container and image)
./docker-run.sh clean
```

### Using Docker Compose

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Restart services
docker-compose restart

# Check status
docker-compose ps
```

### Docker with AWS Credentials

#### Option 1: Mount AWS Credentials (Recommended)

```bash
# Ensure ~/.aws directory exists with credentials
docker run -d \
  --name aws-finops-mcp \
  -v ~/.aws:/home/finops/.aws:ro \
  -e AWS_PROFILE=default \
  -e AWS_REGION=us-east-1 \
  aws-finops-mcp-server:latest
```

#### Option 2: Environment Variables

```bash
docker run -d \
  --name aws-finops-mcp \
  -e AWS_ACCESS_KEY_ID=your-access-key \
  -e AWS_SECRET_ACCESS_KEY=your-secret-key \
  -e AWS_REGION=us-east-1 \
  aws-finops-mcp-server:latest
```

#### Option 3: IAM Role (for EC2/ECS)

```bash
# No credentials needed - uses instance profile
docker run -d \
  --name aws-finops-mcp \
  -e AWS_REGION=us-east-1 \
  aws-finops-mcp-server:latest
```

### Docker Environment Variables

```bash
# AWS Configuration
AWS_PROFILE=default              # AWS profile name
AWS_REGION=us-east-1            # AWS region
AWS_ACCESS_KEY_ID=...           # Access key (not recommended)
AWS_SECRET_ACCESS_KEY=...       # Secret key (not recommended)
AWS_SESSION_TOKEN=...           # Session token (temporary creds)

# Python Configuration
PYTHONUNBUFFERED=1              # Unbuffered output
```

---

## Production Deployment

### Prerequisites

- Python 3.13+
- AWS credentials configured
- Appropriate IAM permissions
- Network access to AWS APIs

### Systemd Service (Linux)

Create `/etc/systemd/system/aws-finops-mcp.service`:

```ini
[Unit]
Description=AWS FinOps MCP Server
After=network.target

[Service]
Type=simple
User=finops
Group=finops
WorkingDirectory=/opt/aws-finops-mcp-server
Environment="PATH=/opt/aws-finops-mcp-server/venv/bin"
Environment="AWS_PROFILE=production"
Environment="AWS_REGION=us-east-1"
ExecStart=/opt/aws-finops-mcp-server/venv/bin/python -m aws_finops_mcp
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable aws-finops-mcp
sudo systemctl start aws-finops-mcp
sudo systemctl status aws-finops-mcp
```

### Supervisor (Alternative)

Create `/etc/supervisor/conf.d/aws-finops-mcp.conf`:

```ini
[program:aws-finops-mcp]
command=/opt/aws-finops-mcp-server/venv/bin/python -m aws_finops_mcp
directory=/opt/aws-finops-mcp-server
user=finops
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/aws-finops-mcp.log
environment=AWS_PROFILE="production",AWS_REGION="us-east-1"
```

Start:

```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start aws-finops-mcp
```

---

## AWS Deployment Options

### 1. EC2 Instance

```bash
# Launch EC2 instance with IAM role
# SSH into instance

# Install dependencies
sudo yum install -y python3.13 git

# Clone repository
git clone <repository-url>
cd aws-finops-mcp-server

# Setup
./setup.sh

# Run with systemd (see above)
```

**IAM Role Required**: Attach IAM role with FinOps permissions to EC2 instance.

### 2. ECS Fargate

Create `task-definition.json`:

```json
{
  "family": "aws-finops-mcp",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "taskRoleArn": "arn:aws:iam::ACCOUNT:role/FinOpsRole",
  "executionRoleArn": "arn:aws:iam::ACCOUNT:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "aws-finops-mcp",
      "image": "aws-finops-mcp-server:latest",
      "essential": true,
      "environment": [
        {
          "name": "AWS_REGION",
          "value": "us-east-1"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/aws-finops-mcp",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

Deploy:

```bash
# Build and push image to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin ACCOUNT.dkr.ecr.us-east-1.amazonaws.com
docker build -t aws-finops-mcp-server .
docker tag aws-finops-mcp-server:latest ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/aws-finops-mcp:latest
docker push ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/aws-finops-mcp:latest

# Register task definition
aws ecs register-task-definition --cli-input-json file://task-definition.json

# Create service
aws ecs create-service \
  --cluster your-cluster \
  --service-name aws-finops-mcp \
  --task-definition aws-finops-mcp \
  --desired-count 1 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx]}"
```

### 3. Lambda (Serverless)

For on-demand execution:

```python
# lambda_handler.py
import json
from aws_finops_mcp.session import get_aws_session
from aws_finops_mcp.tools import cleanup

def lambda_handler(event, context):
    """Lambda handler for AWS FinOps tools."""
    
    # Get parameters from event
    tool = event.get('tool', 'find_unused_lambda_functions')
    region = event.get('region', 'us-east-1')
    period = event.get('period', 90)
    
    # Create session (uses Lambda execution role)
    session = get_aws_session(region_name=region)
    
    # Execute tool
    if tool == 'find_unused_lambda_functions':
        result = cleanup.find_unused_lambda_functions(session, region, period)
    # Add more tools as needed
    
    return {
        'statusCode': 200,
        'body': json.dumps(result)
    }
```

Package and deploy:

```bash
# Create deployment package
pip install -t package/ .
cd package
zip -r ../lambda-deployment.zip .
cd ..
zip -g lambda-deployment.zip lambda_handler.py

# Deploy
aws lambda create-function \
  --function-name aws-finops-mcp \
  --runtime python3.13 \
  --role arn:aws:iam::ACCOUNT:role/FinOpsLambdaRole \
  --handler lambda_handler.lambda_handler \
  --zip-file fileb://lambda-deployment.zip \
  --timeout 300 \
  --memory-size 512
```

### 4. Kubernetes

Create `deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: aws-finops-mcp
  namespace: finops
spec:
  replicas: 1
  selector:
    matchLabels:
      app: aws-finops-mcp
  template:
    metadata:
      labels:
        app: aws-finops-mcp
    spec:
      serviceAccountName: aws-finops-mcp
      containers:
      - name: aws-finops-mcp
        image: aws-finops-mcp-server:latest
        env:
        - name: AWS_REGION
          value: "us-east-1"
        resources:
          requests:
            memory: "256Mi"
            cpu: "500m"
          limits:
            memory: "512Mi"
            cpu: "1000m"
        livenessProbe:
          exec:
            command:
            - python
            - -c
            - "import aws_finops_mcp"
          initialDelaySeconds: 5
          periodSeconds: 30
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: aws-finops-mcp
  namespace: finops
  annotations:
    eks.amazonaws.com/role-arn: arn:aws:iam::ACCOUNT:role/FinOpsRole
```

Deploy:

```bash
kubectl apply -f deployment.yaml
```

---

## Health Checks

### HTTP Health Check (if exposed)

```bash
curl http://localhost:8080/health
```

### Python Health Check

```bash
python -c "import aws_finops_mcp; print('OK')"
```

### Docker Health Check

```bash
docker inspect --format='{{.State.Health.Status}}' aws-finops-mcp
```

---

## Monitoring

### Logs

**Virtual Environment**:
```bash
# Stdout/stderr
python -m aws_finops_mcp 2>&1 | tee server.log
```

**Docker**:
```bash
docker logs -f aws-finops-mcp
```

**Systemd**:
```bash
journalctl -u aws-finops-mcp -f
```

### Metrics

Monitor:
- CPU usage
- Memory usage
- AWS API call rate
- Error rate
- Response time

---

## Security Best Practices

1. **Use IAM Roles** instead of access keys when possible
2. **Least Privilege**: Grant only required permissions
3. **Rotate Credentials** regularly
4. **Network Security**: Use security groups/firewalls
5. **Logging**: Enable CloudTrail for audit
6. **Encryption**: Use encrypted volumes/secrets
7. **Updates**: Keep dependencies updated

---

## Troubleshooting

### Virtual Environment Issues

```bash
# Recreate virtual environment
rm -rf venv
./setup.sh
```

### Docker Issues

```bash
# Check logs
docker logs aws-finops-mcp

# Rebuild image
docker-compose build --no-cache

# Clean up and restart
./docker-run.sh clean
./docker-run.sh run
```

### AWS Credentials Issues

```bash
# Test credentials
aws sts get-caller-identity

# Check IAM permissions
aws iam simulate-principal-policy \
  --policy-source-arn arn:aws:iam::ACCOUNT:role/FinOpsRole \
  --action-names ec2:DescribeInstances
```

---

## Scaling

### Horizontal Scaling

Run multiple instances for different regions:

```bash
# Instance 1: us-east-1
docker run -d --name finops-us-east-1 \
  -e AWS_REGION=us-east-1 \
  aws-finops-mcp-server:latest

# Instance 2: us-west-2
docker run -d --name finops-us-west-2 \
  -e AWS_REGION=us-west-2 \
  aws-finops-mcp-server:latest
```

### Load Balancing

Use a load balancer for multiple MCP server instances if needed.

---

## Backup and Recovery

### Configuration Backup

```bash
# Backup AWS credentials
cp -r ~/.aws ~/.aws.backup

# Backup configuration
tar -czf finops-config-backup.tar.gz \
  ~/.kiro/settings/mcp.json \
  ~/.aws/
```

### Disaster Recovery

1. Keep infrastructure as code (Terraform/CloudFormation)
2. Document deployment procedures
3. Test recovery procedures regularly
4. Maintain configuration backups

---

## Next Steps

1. Choose deployment method based on your needs
2. Configure monitoring and alerting
3. Set up automated backups
4. Document your specific deployment
5. Create runbooks for common operations
