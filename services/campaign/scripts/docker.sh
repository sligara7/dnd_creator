#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Function to print colored messages
print_message() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Check if Docker is running
check_docker() {
    if ! docker info >/dev/null 2>&1; then
        print_message $RED "Docker is not running. Please start Docker first."
        exit 1
    fi
}

# Build all containers
build() {
    print_message $GREEN "Building containers..."
    docker-compose build
}

# Start all containers
start() {
    check_docker
    print_message $GREEN "Starting containers..."
    docker-compose up -d
    print_message $GREEN "Containers started. Services available at:"
    print_message $YELLOW "- Campaign API: http://campaign.localhost"
    print_message $YELLOW "- Grafana: http://localhost:3000"
    print_message $YELLOW "- RabbitMQ Management: http://localhost:15672"
    print_message $YELLOW "- Prometheus: http://localhost:9090"
    print_message $YELLOW "- Traefik Dashboard: http://localhost:8080"
}

# Stop all containers
stop() {
    print_message $GREEN "Stopping containers..."
    docker-compose down
}

# Restart all containers
restart() {
    stop
    start
}

# Show container logs
logs() {
    if [ -z "$2" ]; then
        docker-compose logs -f
    else
        docker-compose logs -f "$2"
    fi
}

# Show container status
status() {
    docker-compose ps
}

# Run database migrations
migrate() {
    print_message $GREEN "Running database migrations..."
    docker-compose exec campaign alembic upgrade head
}

# Clean up Docker resources
clean() {
    print_message $GREEN "Cleaning up Docker resources..."
    docker-compose down -v
    docker system prune -f
}

# Show help message
show_help() {
    echo "Usage: $0 [command]"
    echo
    echo "Commands:"
    echo "  build    - Build all containers"
    echo "  start    - Start all containers"
    echo "  stop     - Stop all containers"
    echo "  restart  - Restart all containers"
    echo "  logs     - Show container logs (use 'logs [container]' for specific container)"
    echo "  status   - Show container status"
    echo "  migrate  - Run database migrations"
    echo "  clean    - Clean up Docker resources"
    echo "  help     - Show this help message"
}

# Main script logic
case "$1" in
    build)
        build
        ;;
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    logs)
        logs "$@"
        ;;
    status)
        status
        ;;
    migrate)
        migrate
        ;;
    clean)
        clean
        ;;
    help)
        show_help
        ;;
    *)
        print_message $RED "Unknown command: $1"
        show_help
        exit 1
        ;;
esac

exit 0
