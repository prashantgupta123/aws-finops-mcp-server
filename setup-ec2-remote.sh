#!/bin/bash
# Setup script for AWS FinOps MCP Server on EC2 with remote access

set -e

echo "=========================================="
echo "AWS FinOps MCP Server - EC2 Remote Setup"
echo "=========================================="
echo ""

# Configuration
INSTALL_NGINX="${1:-no}"  # yes/no
SETUP_SSL="${2:-no}"      # yes/no
DOMAIN="${3:-}"           # your-domain.com

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Helper functions
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

# Check if running on EC2
print_info "Checking if running on EC2..."
if curl -s -m 2 http://169.254.169.254/latest/meta-data/instance-id > /dev/null 2>&1; then
    INSTANCE_ID=$(curl -s http://169.254.169.254/latest/meta-data/instance-id)
    PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)
    print_success "Running on EC2 instance: $INSTANCE_ID"
    print_info "Public IP: $PUBLIC_IP"
else
    print_info "Not running on EC2 (or metadata service not available)"
fi

echo ""
echo "Step 1: Updating system packages..."
sudo yum update -y || sudo apt-get update -y
print_success "System updated"

echo ""
echo "Step 2: Installing Docker..."
if ! command -v docker &> /dev/null; then
    # Amazon Linux 2 / RHEL
    if command -v yum &> /dev/null; then
        sudo yum install -y docker
        sudo systemctl start docker
        sudo systemctl enable docker
        sudo usermod -a -G docker $USER
    # Ubuntu / Debian
    elif command -v apt-get &> /dev/null; then
        sudo apt-get install -y docker.io
        sudo systemctl start docker
        sudo systemctl enable docker
        sudo usermod -a -G docker $USER
    fi
    print_success "Docker installed"
else
    print_success "Docker already installed"
fi

echo ""
echo "Step 3: Installing Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    print_success "Docker Compose installed"
else
    print_success "Docker Compose already installed"
fi

echo ""
echo "Step 4: Setting up MCP server..."
if [ ! -d "aws-finops-mcp-server" ]; then
    print_info "Please clone the repository first:"
    print_info "git clone https://github.com/your-repo/aws-finops-mcp-server.git"
    print_info "cd aws-finops-mcp-server"
    print_info "Then run this script again"
    exit 1
fi

# Create environment file
cat > .env <<EOF
# MCP Server Configuration
MCP_SERVER_MODE=http
MCP_SERVER_HOST=0.0.0.0
MCP_SERVER_PORT=8000

# AWS Configuration
AWS_REGION=us-east-1
# AWS_PROFILE=default  # Uncomment if using AWS profile

# Logging
PYTHONUNBUFFERED=1
EOF

print_success "Environment file created"

echo ""
echo "Step 5: Starting MCP server..."
# Use HTTP mode docker-compose
docker-compose -f docker-compose-http.yml up -d
print_success "MCP server started"

# Wait for server to be ready
echo ""
print_info "Waiting for server to be ready..."
sleep 5

# Test server
if curl -s http://localhost:8000/health > /dev/null; then
    print_success "Server is healthy!"
else
    print_error "Server health check failed"
fi

# Install Nginx if requested
if [ "$INSTALL_NGINX" = "yes" ]; then
    echo ""
    echo "Step 6: Installing Nginx..."
    
    if command -v yum &> /dev/null; then
        sudo yum install -y nginx
    elif command -v apt-get &> /dev/null; then
        sudo apt-get install -y nginx
    fi
    
    # Create Nginx configuration
    sudo tee /etc/nginx/conf.d/finops-mcp.conf > /dev/null <<'NGINX_EOF'
upstream mcp_backend {
    server localhost:8000;
}

server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://mcp_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
NGINX_EOF
    
    # Start Nginx
    sudo systemctl start nginx
    sudo systemctl enable nginx
    
    print_success "Nginx installed and configured"
    
    # Setup SSL if requested
    if [ "$SETUP_SSL" = "yes" ] && [ -n "$DOMAIN" ]; then
        echo ""
        echo "Step 7: Setting up SSL with Let's Encrypt..."
        
        # Install certbot
        if command -v yum &> /dev/null; then
            sudo yum install -y certbot python3-certbot-nginx
        elif command -v apt-get &> /dev/null; then
            sudo apt-get install -y certbot python3-certbot-nginx
        fi
        
        # Get certificate
        sudo certbot --nginx -d "$DOMAIN" --non-interactive --agree-tos --email admin@"$DOMAIN"
        
        # Setup auto-renewal
        sudo systemctl enable certbot-renew.timer || (crontab -l 2>/dev/null; echo "0 0 * * * certbot renew --quiet") | crontab -
        
        print_success "SSL certificate installed"
    fi
fi

echo ""
echo "=========================================="
echo "✅ Setup Complete!"
echo "=========================================="
echo ""

# Display connection information
echo "📊 Server Information:"
echo "  - Container: aws-finops-mcp-http"
echo "  - Local URL: http://localhost:8000"
if [ -n "$PUBLIC_IP" ]; then
    echo "  - Public IP: $PUBLIC_IP"
fi
if [ "$INSTALL_NGINX" = "yes" ]; then
    echo "  - Nginx: Installed"
    if [ "$SETUP_SSL" = "yes" ] && [ -n "$DOMAIN" ]; then
        echo "  - Public URL: https://$DOMAIN"
    elif [ -n "$PUBLIC_IP" ]; then
        echo "  - Public URL: http://$PUBLIC_IP"
    fi
fi
echo ""

echo "🔧 Useful Commands:"
echo "  - View logs: docker-compose -f docker-compose-http.yml logs -f"
echo "  - Stop server: docker-compose -f docker-compose-http.yml down"
echo "  - Restart server: docker-compose -f docker-compose-http.yml restart"
echo "  - Health check: curl http://localhost:8000/health"
echo ""

echo "🔒 Security Recommendations:"
echo "  1. Configure EC2 security group to allow only your IP"
echo "  2. Use SSH tunnel for development: ssh -L 8000:localhost:8000 ec2-user@$PUBLIC_IP"
echo "  3. For production, use HTTPS with Nginx and SSL certificate"
echo "  4. Enable CloudWatch logging for monitoring"
echo ""

echo "📚 Next Steps:"
echo "  1. Test the server: curl http://localhost:8000/health"
echo "  2. List tools: curl http://localhost:8000/tools"
echo "  3. Configure your MCP client to connect"
echo "  4. See REMOTE_ACCESS_GUIDE.md for detailed instructions"
echo ""

print_success "AWS FinOps MCP Server is ready!"
