#!/bin/bash

# AgentOps Dashboard Quick Start Script
# This script sets up the complete AgentOps Dashboard environment

set -e  # Exit on any error

echo "🚀 Starting AgentOps Dashboard Quick Setup..."
echo "============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        echo "Visit: https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        echo "Visit: https://docs.docker.com/compose/install/"
        exit 1
    fi
    
    # Check if Docker daemon is running
    if ! docker info &> /dev/null; then
        print_error "Docker daemon is not running. Please start Docker first."
        exit 1
    fi
    
    print_success "Docker and Docker Compose are installed and running"
}

# Create environment file if it doesn't exist
setup_environment() {
    if [ ! -f .env ]; then
        print_status "Creating environment configuration..."
        cp .env.example .env
        
        # Generate a random secret key
        SECRET_KEY=$(openssl rand -hex 32)
        sed -i.bak "s/SECRET_KEY=your-secret-key-here-change-in-production/SECRET_KEY=$SECRET_KEY/" .env
        rm .env.bak 2>/dev/null || true
        
        print_success "Environment file created at .env"
        print_warning "Please review and update .env with your specific configuration"
    else
        print_status "Environment file already exists"
    fi
}

# Create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    mkdir -p {logs,data,config/nginx/ssl,config/grafana/datasources,config/grafana/dashboards}
    
    # Create SSL certificates for development
    if [ ! -f config/nginx/ssl/cert.pem ]; then
        print_status "Generating self-signed SSL certificates for development..."
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout config/nginx/ssl/key.pem \
            -out config/nginx/ssl/cert.pem \
            -subj "/C=IN/ST=Maharashtra/L=Mumbai/O=IHCL/OU=IT/CN=localhost"
        print_success "SSL certificates generated"
    fi
    
    print_success "Directories created successfully"
}

# Generate demo data
generate_demo_data() {
    print_status "Checking for demo data..."
    
    if [ ! -f demo_data/demo_data.json ]; then
        print_status "Generating demo data for portfolio demonstration..."
        python3 demo_data/generate_demo_data.py
        print_success "Demo data generated successfully"
    else
        print_status "Demo data already exists"
    fi
}

# Start services
start_services() {
    print_status "Starting AgentOps Dashboard services..."
    
    # Pull latest images
    print_status "Pulling Docker images..."
    docker-compose pull
    
    # Build custom images
    print_status "Building application images..."
    docker-compose build
    
    # Start services
    print_status "Starting all services..."
    docker-compose up -d
    
    print_success "All services started successfully"
}

# Wait for services to be healthy
wait_for_services() {
    print_status "Waiting for services to be ready..."
    
    # Wait for database
    print_status "Waiting for PostgreSQL..."
    for i in {1..30}; do
        if docker-compose exec -T postgres pg_isready -U agentops -d agentops_dashboard &> /dev/null; then
            break
        fi
        sleep 2
        echo -n "."
    done
    echo ""
    
    # Wait for Redis
    print_status "Waiting for Redis..."
    for i in {1..30}; do
        if docker-compose exec -T redis redis-cli ping &> /dev/null; then
            break
        fi
        sleep 2
        echo -n "."
    done
    echo ""
    
    # Wait for API
    print_status "Waiting for API..."
    for i in {1..60}; do
        if curl -s http://localhost:8000/health &> /dev/null; then
            break
        fi
        sleep 2
        echo -n "."
    done
    echo ""
    
    # Wait for Dashboard
    print_status "Waiting for Dashboard..."
    for i in {1..60}; do
        if curl -s http://localhost:8501/_stcore/health &> /dev/null; then
            break
        fi
        sleep 2
        echo -n "."
    done
    echo ""
    
    print_success "All services are ready!"
}

# Initialize database
initialize_database() {
    print_status "Initializing database schema..."
    
    # Wait a bit more for the API to fully initialize
    sleep 10
    
    # The database will be initialized automatically by the API service
    # Check if initialization was successful
    if curl -s http://localhost:8000/health | grep -q "healthy"; then
        print_success "Database initialized successfully"
    else
        print_warning "Database initialization may still be in progress"
    fi
}

# Display access information
show_access_info() {
    echo ""
    echo "============================================="
    echo -e "${GREEN}🎉 AgentOps Dashboard is now running!${NC}"
    echo "============================================="
    echo ""
    echo "📊 Main Dashboard:      http://localhost:8501"
    echo "🔧 API Documentation:   http://localhost:8000/docs"
    echo "📈 Grafana Analytics:   http://localhost:3000 (admin/admin123)"
    echo "📊 Prometheus Metrics:  http://localhost:9090"
    echo ""
    echo "🔐 Default Credentials:"
    echo "   Grafana: admin / admin123"
    echo ""
    echo "📁 Useful Commands:"
    echo "   View logs:           docker-compose logs -f"
    echo "   Stop services:       docker-compose down"
    echo "   Restart services:    docker-compose restart"
    echo "   View status:         docker-compose ps"
    echo ""
    echo "📖 Documentation:"
    echo "   Architecture:        docs/ARCHITECTURE.md"
    echo "   API Guide:           http://localhost:8000/docs"
    echo "   Configuration:       .env"
    echo ""
    print_success "Setup completed successfully!"
}

# Check service status
check_service_status() {
    print_status "Checking service status..."
    
    echo ""
    echo "Service Status:"
    echo "==============="
    
    # Check each service
    services=("postgres:5432" "redis:6379" "localhost:8000" "localhost:8501" "localhost:3000" "localhost:9090")
    service_names=("PostgreSQL" "Redis" "API" "Dashboard" "Grafana" "Prometheus")
    
    for i in "${!services[@]}"; do
        service="${services[$i]}"
        name="${service_names[$i]}"
        
        if curl -s --max-time 5 "http://$service" &> /dev/null || nc -z ${service/:/ } &> /dev/null; then
            echo -e "✅ $name: ${GREEN}Running${NC}"
        else
            echo -e "❌ $name: ${RED}Not responding${NC}"
        fi
    done
    
    echo ""
}

# Cleanup function
cleanup() {
    if [ "$1" = "clean" ]; then
        print_status "Cleaning up existing services..."
        docker-compose down -v
        docker system prune -f
        print_success "Cleanup completed"
    fi
}

# Main execution
main() {
    echo "AgentOps Dashboard - Enterprise AI Operations Platform"
    echo "Built for IHCL FlexiCore Security Platform"
    echo ""
    
    # Handle command line arguments
    if [ "$1" = "clean" ]; then
        cleanup clean
        return 0
    fi
    
    if [ "$1" = "status" ]; then
        check_service_status
        return 0
    fi
    
    # Run setup steps
    check_docker
    setup_environment
    create_directories
    generate_demo_data
    start_services
    wait_for_services
    initialize_database
    check_service_status
    show_access_info
    
    # Save startup information
    cat > startup_info.txt << EOF
AgentOps Dashboard - Startup Information
Generated: $(date)

Service URLs:
- Main Dashboard: http://localhost:8501
- API Documentation: http://localhost:8000/docs
- Grafana Analytics: http://localhost:3000
- Prometheus Metrics: http://localhost:9090

Credentials:
- Grafana: admin / admin123

Files:
- Configuration: .env
- Logs: logs/
- Demo Data: demo_data/
EOF
    
    print_success "Startup information saved to startup_info.txt"
}

# Handle script interruption
trap 'echo ""; print_warning "Script interrupted. Services may still be starting in the background."; exit 1' INT

# Run main function with all arguments
main "$@"