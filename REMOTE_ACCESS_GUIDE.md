# Remote Access Guide - AWS FinOps MCP Server

How to run the MCP server on EC2 Docker and connect from remote clients.

## 🎯 Architecture Overview

```
┌─────────────────┐         ┌──────────────────────┐
│  Remote Client  │         │   EC2 Instance       │
│  (Your Laptop)  │────────▶│  ┌────────────────┐  │
│                 │  HTTPS  │  │ Docker         │  │
│  - Kiro         │  or     │  │ ┌────────────┐ │  │
│  - Claude       │  SSH    │  │ │ MCP Server │ │  │
│  - Other MCP    │         │  │ └────────────┘ │  │
│    Clients      │         │  └────────────────┘  │
└─────────────────┘         └──────────────────────┘
```

## 🔧 Setup Options

### Option 1: SSH Tunnel (Recommended for Security)

**Pros**: Secure, no public exposure, uses existing SSH access  
**Cons**: Requires SSH connection to be active

#### Step 1: Update Docker Configuration

The MCP server needs to expose a port. Update `docker-compose.yml`:

```yaml
version: '3.8'

services:
  aws-finops-mcp:
    build: .
    container_name: aws-finops-mcp
    ports:
      - "127.0.0.1:8000:8000"  # Bind to localhost only
    environment:
      - AWS_REGION=us-east-1
      - MCP_SERVER_HOST=0.0.0.0
      - MCP_SERVER_PORT=8000
    restart: unless-stopped
```

#### Step 2: Run on EC2

```bash
# SSH into EC2
ssh -i your-key.pem ec2-user@your-ec2-ip

# Start the server
cd aws-finops-mcp-server
docker-compose up -d

# Verify it's running
docker-compose logs -f
```

#### Step 3: Create SSH Tunnel from Client

```bash
# On your local machine
ssh -i your-key.pem -L 8000:localhost:8000 ec2-user@your-ec2-ip -N

# This forwards local port 8000 to EC2's port 8000
# Keep this terminal open
```

#### Step 4: Configure MCP Client

On your local machine, configure your MCP client to connect to `localhost:8000`:

```json
{
  "mcpServers": {
    "aws-finops": {
      "command": "curl",
      "args": [
        "-X", "POST",
        "http://localhost:8000/mcp",
        "-H", "Content-Type: application/json",
        "-d", "@-"
      ]
    }
  }
}
```

---

### Option 2: HTTPS with Nginx Reverse Proxy (Production)

**Pros**: Secure, professional, supports multiple clients  
**Cons**: Requires SSL certificate, more setup

#### Step 1: Install Nginx on EC2

```bash
# Amazon Linux 2
sudo yum install -y nginx

# Ubuntu
sudo apt-get install -y nginx
```

#### Step 2: Configure Nginx

Create `/etc/nginx/conf.d/finops-mcp.conf`:

```nginx
upstream mcp_backend {
    server localhost:8000;
}

server {
    listen 80;
    server_name your-domain.com;  # or EC2 public IP

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    # SSL certificates (use Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;

    # Authentication (basic auth)
    auth_basic "MCP Server";
    auth_basic_user_file /etc/nginx/.htpasswd;

    location / {
        proxy_pass http://mcp_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support (if needed)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

#### Step 3: Setup SSL with Let's Encrypt

```bash
# Install certbot
sudo yum install -y certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo systemctl enable certbot-renew.timer
```

#### Step 4: Create Basic Auth

```bash
# Install htpasswd
sudo yum install -y httpd-tools

# Create password file
sudo htpasswd -c /etc/nginx/.htpasswd finops-user

# Enter password when prompted
```

#### Step 5: Start Nginx

```bash
sudo systemctl start nginx
sudo systemctl enable nginx
```

#### Step 6: Update Security Group

Add inbound rules:
- Port 80 (HTTP) - from your IP
- Port 443 (HTTPS) - from your IP

#### Step 7: Configure MCP Client

```json
{
  "mcpServers": {
    "aws-finops": {
      "command": "curl",
      "args": [
        "-X", "POST",
        "https://your-domain.com/mcp",
        "-H", "Content-Type: application/json",
        "-H", "Authorization: Basic base64(username:password)",
        "-d", "@-"
      ]
    }
  }
}
```

---

### Option 3: AWS Systems Manager Session Manager (No SSH)

**Pros**: No SSH keys, no open ports, AWS native  
**Cons**: Requires SSM agent, AWS CLI

#### Step 1: Install SSM Agent on EC2

```bash
# Amazon Linux 2 (usually pre-installed)
sudo yum install -y amazon-ssm-agent
sudo systemctl start amazon-ssm-agent
```

#### Step 2: Add IAM Role to EC2

Attach `AmazonSSMManagedInstanceCore` policy to EC2 instance role.

#### Step 3: Start Port Forwarding

```bash
# On your local machine
aws ssm start-session \
  --target i-your-instance-id \
  --document-name AWS-StartPortForwardingSession \
  --parameters '{"portNumber":["8000"],"localPortNumber":["8000"]}'
```

#### Step 4: Configure MCP Client

Same as SSH tunnel option - connect to `localhost:8000`.

---

### Option 4: API Gateway + Lambda (Serverless)

**Pros**: Fully managed, auto-scaling, no EC2 management  
**Cons**: Different architecture, requires code changes

See `DEPLOYMENT.md` for Lambda deployment details.

---

## 🔒 Security Considerations

### 1. Network Security

**EC2 Security Group**:
```bash
# Allow only your IP
aws ec2 authorize-security-group-ingress \
  --group-id sg-xxxxx \
  --protocol tcp \
  --port 443 \
  --cidr YOUR_IP/32
```

**VPC Configuration**:
- Place EC2 in private subnet
- Use NAT Gateway for outbound
- Use Application Load Balancer in public subnet

### 2. Authentication

**Option A: API Key**:
```bash
# Add to Nginx config
if ($http_x_api_key != "your-secret-key") {
    return 401;
}
```

**Option B: AWS IAM Authentication**:
```bash
# Use AWS Signature V4
# Client signs requests with AWS credentials
```

**Option C: OAuth 2.0**:
```bash
# Use AWS Cognito or other OAuth provider
```

### 3. Encryption

- ✅ Use HTTPS/TLS for all connections
- ✅ Use SSH tunnel for development
- ✅ Never expose HTTP port publicly
- ✅ Use AWS Certificate Manager for SSL

### 4. Monitoring

**CloudWatch Logs**:
```bash
# Configure Docker to send logs to CloudWatch
docker run \
  --log-driver=awslogs \
  --log-opt awslogs-group=/aws/ecs/finops-mcp \
  --log-opt awslogs-region=us-east-1 \
  your-image
```

**CloudWatch Alarms**:
```bash
# Alert on high error rates
aws cloudwatch put-metric-alarm \
  --alarm-name finops-mcp-errors \
  --metric-name ErrorCount \
  --threshold 10
```

---

## 📝 Complete Setup Example

### EC2 Setup Script

```bash
#!/bin/bash
# setup-ec2-mcp-server.sh

set -e

echo "Setting up AWS FinOps MCP Server on EC2..."

# Update system
sudo yum update -y

# Install Docker
sudo yum install -y docker
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -a -G docker ec2-user

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Clone repository
git clone https://github.com/your-repo/aws-finops-mcp-server.git
cd aws-finops-mcp-server

# Create environment file
cat > .env <<EOF
AWS_REGION=us-east-1
MCP_SERVER_HOST=0.0.0.0
MCP_SERVER_PORT=8000
EOF

# Start services
docker-compose up -d

# Install Nginx
sudo yum install -y nginx

# Configure Nginx (basic)
sudo tee /etc/nginx/conf.d/finops-mcp.conf <<EOF
server {
    listen 80;
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
}
EOF

# Start Nginx
sudo systemctl start nginx
sudo systemctl enable nginx

echo "✅ Setup complete!"
echo "Server running on port 8000"
echo "Nginx proxy on port 80"
```

### Client Configuration

```json
{
  "mcpServers": {
    "aws-finops-remote": {
      "command": "ssh",
      "args": [
        "-i", "~/.ssh/your-key.pem",
        "-L", "8000:localhost:8000",
        "ec2-user@your-ec2-ip",
        "docker", "exec", "-i", "aws-finops-mcp",
        "python", "-m", "aws_finops_mcp"
      ]
    }
  }
}
```

---

## 🧪 Testing Remote Connection

### Test 1: Check Server is Running

```bash
# On EC2
docker-compose ps
docker-compose logs

# Should show server running on port 8000
```

### Test 2: Test Local Connection

```bash
# On EC2
curl http://localhost:8000/health

# Should return: {"status": "healthy"}
```

### Test 3: Test Remote Connection

```bash
# From your laptop (with SSH tunnel active)
curl http://localhost:8000/health

# Should return: {"status": "healthy"}
```

### Test 4: Test MCP Tool

```bash
# From your laptop
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "find_unused_lambda_functions",
    "arguments": {
      "region_name": "us-east-1",
      "period": 90
    }
  }'
```

---

## 🚨 Troubleshooting

### Issue: Connection Refused

**Check**:
```bash
# On EC2
docker-compose ps  # Is container running?
docker-compose logs  # Any errors?
netstat -tlnp | grep 8000  # Is port listening?
```

**Solution**: Restart container
```bash
docker-compose restart
```

### Issue: SSH Tunnel Not Working

**Check**:
```bash
# On local machine
ps aux | grep ssh  # Is tunnel running?
netstat -an | grep 8000  # Is port forwarded?
```

**Solution**: Restart tunnel
```bash
# Kill existing tunnel
pkill -f "ssh.*8000"

# Start new tunnel
ssh -i your-key.pem -L 8000:localhost:8000 ec2-user@your-ec2-ip -N
```

### Issue: Security Group Blocking

**Check**:
```bash
# List security group rules
aws ec2 describe-security-groups --group-ids sg-xxxxx
```

**Solution**: Add your IP
```bash
aws ec2 authorize-security-group-ingress \
  --group-id sg-xxxxx \
  --protocol tcp \
  --port 443 \
  --cidr YOUR_IP/32
```

### Issue: SSL Certificate Error

**Check**:
```bash
# Test SSL
openssl s_client -connect your-domain.com:443
```

**Solution**: Renew certificate
```bash
sudo certbot renew
sudo systemctl reload nginx
```

---

## 📊 Recommended Architecture

### Development
```
Your Laptop → SSH Tunnel → EC2 Docker → MCP Server
```

### Production
```
Your Laptop → HTTPS → ALB → EC2 Docker → MCP Server
              ↓
         CloudWatch
              ↓
         Alarms/Logs
```

### Enterprise
```
Your Laptop → VPN → Private ALB → ECS Fargate → MCP Server
                                        ↓
                                   CloudWatch
                                        ↓
                                   X-Ray Tracing
```

---

## 📚 Additional Resources

- **SSH Tunneling**: [AWS SSH Tunnel Guide](https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-working-with-sessions-start.html)
- **Nginx Configuration**: [Nginx Reverse Proxy](https://docs.nginx.com/nginx/admin-guide/web-server/reverse-proxy/)
- **Let's Encrypt**: [Certbot Documentation](https://certbot.eff.org/)
- **AWS Systems Manager**: [Session Manager](https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager.html)

---

## ✅ Summary

### Best Practices

1. ✅ **Use SSH tunnel** for development
2. ✅ **Use HTTPS + Nginx** for production
3. ✅ **Use AWS Systems Manager** for no-SSH access
4. ✅ **Never expose HTTP** publicly
5. ✅ **Always use authentication**
6. ✅ **Monitor with CloudWatch**
7. ✅ **Restrict security groups** to your IP

### Quick Start

```bash
# On EC2
docker-compose up -d

# On your laptop
ssh -i key.pem -L 8000:localhost:8000 ec2-user@ec2-ip -N

# Test
curl http://localhost:8000/health
```

---

**Last Updated**: January 22, 2026  
**Version**: 1.0
