#!/bin/bash
# AWS FinOps MCP Server - Docker Run Script
# This script builds and runs the MCP server in Docker

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

IMAGE_NAME="aws-finops-mcp-server"
CONTAINER_NAME="aws-finops-mcp"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}AWS FinOps MCP Server - Docker${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Function to show usage
show_usage() {
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  build       Build the Docker image"
    echo "  run         Run the container"
    echo "  start       Start the container (if stopped)"
    echo "  stop        Stop the container"
    echo "  restart     Restart the container"
    echo "  logs        Show container logs"
    echo "  shell       Open a shell in the container"
    echo "  clean       Remove container and image"
    echo "  status      Show container status"
    echo ""
    echo "Examples:"
    echo "  $0 build"
    echo "  $0 run"
    echo "  $0 logs"
}

# Function to build image
build_image() {
    echo -e "${YELLOW}Building Docker image...${NC}"
    docker build -t "$IMAGE_NAME:latest" .
    echo -e "${GREEN}✓ Image built successfully${NC}"
}

# Function to run container
run_container() {
    # Check if container already exists
    if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        echo -e "${YELLOW}Container already exists. Removing...${NC}"
        docker rm -f "$CONTAINER_NAME" > /dev/null 2>&1
    fi
    
    echo -e "${YELLOW}Starting container...${NC}"
    
    # Check if AWS credentials exist
    if [ ! -d "$HOME/.aws" ]; then
        echo -e "${RED}Warning: AWS credentials not found at ~/.aws${NC}"
        echo -e "${YELLOW}You can configure them later or use environment variables${NC}"
    fi
    
    # Run with docker-compose
    if [ -f "docker-compose.yml" ]; then
        docker-compose up -d
    else
        # Fallback to docker run
        docker run -d \
            --name "$CONTAINER_NAME" \
            --restart unless-stopped \
            -e AWS_PROFILE="${AWS_PROFILE:-default}" \
            -e AWS_REGION="${AWS_REGION:-us-east-1}" \
            -v "$HOME/.aws:/home/finops/.aws:ro" \
            --network host \
            "$IMAGE_NAME:latest"
    fi
    
    echo -e "${GREEN}✓ Container started${NC}"
    echo ""
    echo -e "Container name: ${BLUE}$CONTAINER_NAME${NC}"
    echo -e "View logs: ${YELLOW}$0 logs${NC}"
}

# Function to stop container
stop_container() {
    echo -e "${YELLOW}Stopping container...${NC}"
    if docker-compose ps | grep -q "$CONTAINER_NAME"; then
        docker-compose down
    else
        docker stop "$CONTAINER_NAME" > /dev/null 2>&1 || true
    fi
    echo -e "${GREEN}✓ Container stopped${NC}"
}

# Function to start container
start_container() {
    echo -e "${YELLOW}Starting container...${NC}"
    if [ -f "docker-compose.yml" ]; then
        docker-compose start
    else
        docker start "$CONTAINER_NAME"
    fi
    echo -e "${GREEN}✓ Container started${NC}"
}

# Function to restart container
restart_container() {
    echo -e "${YELLOW}Restarting container...${NC}"
    if [ -f "docker-compose.yml" ]; then
        docker-compose restart
    else
        docker restart "$CONTAINER_NAME"
    fi
    echo -e "${GREEN}✓ Container restarted${NC}"
}

# Function to show logs
show_logs() {
    echo -e "${YELLOW}Showing container logs (Ctrl+C to exit)...${NC}"
    echo ""
    if [ -f "docker-compose.yml" ]; then
        docker-compose logs -f
    else
        docker logs -f "$CONTAINER_NAME"
    fi
}

# Function to open shell
open_shell() {
    echo -e "${YELLOW}Opening shell in container...${NC}"
    docker exec -it "$CONTAINER_NAME" /bin/bash
}

# Function to clean up
clean_up() {
    echo -e "${YELLOW}Cleaning up...${NC}"
    
    # Stop and remove container
    if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        docker rm -f "$CONTAINER_NAME" > /dev/null 2>&1
        echo -e "${GREEN}✓ Container removed${NC}"
    fi
    
    # Remove image
    if docker images --format '{{.Repository}}' | grep -q "^${IMAGE_NAME}$"; then
        docker rmi "$IMAGE_NAME:latest" > /dev/null 2>&1
        echo -e "${GREEN}✓ Image removed${NC}"
    fi
    
    # Clean up docker-compose
    if [ -f "docker-compose.yml" ]; then
        docker-compose down -v > /dev/null 2>&1 || true
    fi
    
    echo -e "${GREEN}✓ Cleanup complete${NC}"
}

# Function to show status
show_status() {
    echo -e "${YELLOW}Container Status:${NC}"
    echo ""
    
    if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        echo -e "Status: ${GREEN}Running${NC}"
        docker ps --filter "name=$CONTAINER_NAME" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    elif docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        echo -e "Status: ${YELLOW}Stopped${NC}"
        docker ps -a --filter "name=$CONTAINER_NAME" --format "table {{.Names}}\t{{.Status}}"
    else
        echo -e "Status: ${RED}Not found${NC}"
    fi
    
    echo ""
    
    # Show image info
    if docker images --format '{{.Repository}}' | grep -q "^${IMAGE_NAME}$"; then
        echo -e "${YELLOW}Image Info:${NC}"
        docker images "$IMAGE_NAME" --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"
    fi
}

# Main script
case "${1:-}" in
    build)
        build_image
        ;;
    run)
        build_image
        run_container
        show_status
        ;;
    start)
        start_container
        ;;
    stop)
        stop_container
        ;;
    restart)
        restart_container
        ;;
    logs)
        show_logs
        ;;
    shell)
        open_shell
        ;;
    clean)
        clean_up
        ;;
    status)
        show_status
        ;;
    *)
        show_usage
        exit 1
        ;;
esac

echo ""
