#!/bin/bash
# D&D Character Creator - Podman Setup Script

set -e

echo "🎲 D&D Character Creator - Podman Setup"
echo "======================================="

# Check if podman is installed
if ! command -v podman &> /dev/null; then
    echo "❌ Podman is not installed!"
    echo "Install Podman:"
    echo "  - Ubuntu/Debian: sudo apt-get install podman"
    echo "  - RHEL/CentOS/Fedora: sudo dnf install podman"
    echo "  - Arch: sudo pacman -S podman"
    exit 1
fi

# Check if podman-compose is available
if ! command -v podman-compose &> /dev/null; then
    echo "⚠️  podman-compose not found. Installing..."
    pip3 install podman-compose
fi

echo "✅ Podman version: $(podman --version)"
echo "✅ Podman-compose available"

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs
mkdir -p sql

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📋 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your API keys and settings!"
    echo "   nano .env"
else
    echo "✅ .env file exists"
fi

# Create SQL initialization file
if [ ! -f sql/init.sql ]; then
    echo "🗄️  Creating database initialization script..."
    cat > sql/init.sql << 'EOF'
-- D&D Character Creator Database Initialization
CREATE DATABASE IF NOT EXISTS dnd_characters;

-- Create additional indexes for performance
\c dnd_characters;

-- Index on character name for faster searches
-- (Will be created by SQLAlchemy migrations)

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE dnd_characters TO dnd_user;

EOF
    echo "✅ Database initialization script created"
fi

# Function to build and run with podman-compose
run_with_podman_compose() {
    echo "🐋 Using podman-compose..."
    podman-compose -f podman-compose.yml "$@"
}

# Function to run with podman commands directly
run_with_podman_direct() {
    echo "🐋 Using direct podman commands..."
    
    case "$1" in
        "up")
            # Create network
            podman network create dnd_network 2>/dev/null || true
            
            # Create volume
            podman volume create postgres_data 2>/dev/null || true
            
            # Start database
            echo "🗄️  Starting PostgreSQL database..."
            podman run -d \
                --name dnd_character_db \
                --network dnd_network \
                -e POSTGRES_DB=dnd_characters \
                -e POSTGRES_USER=dnd_user \
                -e POSTGRES_PASSWORD="${DB_PASSWORD:-change_this_password}" \
                -v postgres_data:/var/lib/postgresql/data \
                -v "$(pwd)/sql/init.sql:/docker-entrypoint-initdb.d/init.sql" \
                -p 5432:5432 \
                postgres:15-alpine
            
            # Wait for database to be ready
            echo "⏳ Waiting for database to be ready..."
            sleep 10
            
            # Build API image
            echo "🔨 Building API image..."
            podman build -f Dockerfile.new -t dnd-character-api .
            
            # Start API
            echo "🚀 Starting API service..."
            podman run -d \
                --name dnd_character_api \
                --network dnd_network \
                --env-file .env \
                -e DATABASE_URL="postgresql://dnd_user:${DB_PASSWORD:-change_this_password}@dnd_character_db:5432/dnd_characters" \
                -v "$(pwd)/logs:/app/logs" \
                -p 8000:8000 \
                dnd-character-api
            ;;
        "down")
            echo "🛑 Stopping services..."
            podman stop dnd_character_api dnd_character_db 2>/dev/null || true
            podman rm dnd_character_api dnd_character_db 2>/dev/null || true
            ;;
        "logs")
            podman logs -f "${2:-dnd_character_api}"
            ;;
        "build")
            podman build -f Dockerfile.new -t dnd-character-api .
            ;;
        *)
            echo "Usage: $0 {up|down|logs|build}"
            exit 1
            ;;
    esac
}

# Main execution
case "${1:-help}" in
    "setup")
        echo "✅ Setup complete!"
        echo ""
        echo "Next steps:"
        echo "1. Edit .env file with your settings: nano .env"
        echo "2. Start services: ./podman-setup.sh up"
        echo "3. Check status: ./podman-setup.sh status"
        ;;
    "up")
        shift
        if command -v podman-compose &> /dev/null; then
            run_with_podman_compose up --build "$@"
        else
            run_with_podman_direct up
        fi
        echo ""
        echo "🎉 Services started!"
        echo "📍 API: http://localhost:8000"
        echo "📍 API Docs: http://localhost:8000/docs"
        echo "📍 Health: http://localhost:8000/health"
        ;;
    "down")
        if command -v podman-compose &> /dev/null; then
            run_with_podman_compose down
        else
            run_with_podman_direct down
        fi
        echo "🛑 Services stopped"
        ;;
    "logs")
        service="${2:-api}"
        if command -v podman-compose &> /dev/null; then
            run_with_podman_compose logs -f "$service"
        else
            run_with_podman_direct logs "$service"
        fi
        ;;
    "build")
        if command -v podman-compose &> /dev/null; then
            run_with_podman_compose build
        else
            run_with_podman_direct build
        fi
        ;;
    "status")
        echo "📊 Container Status:"
        podman ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
        echo ""
        echo "🌐 Network Status:"
        podman network ls | grep dnd || echo "No dnd_network found"
        echo ""
        echo "💾 Volume Status:"
        podman volume ls | grep postgres || echo "No postgres_data volume found"
        ;;
    "shell")
        service="${2:-api}"
        case "$service" in
            "api")
                podman exec -it dnd_character_api /bin/bash
                ;;
            "db"|"database")
                podman exec -it dnd_character_db psql -U dnd_user -d dnd_characters
                ;;
            *)
                echo "Available shells: api, db"
                ;;
        esac
        ;;
    "test")
        echo "🧪 Testing API endpoints..."
        echo "Health check:"
        curl -s http://localhost:8000/health | jq . || echo "API not responding"
        echo ""
        echo "Root endpoint:"
        curl -s http://localhost:8000/ | jq . || echo "API not responding"
        ;;
    "clean")
        echo "🧹 Cleaning up containers, images, and volumes..."
        podman stop $(podman ps -aq) 2>/dev/null || true
        podman rm $(podman ps -aq) 2>/dev/null || true
        podman rmi dnd-character-api 2>/dev/null || true
        podman volume rm postgres_data 2>/dev/null || true
        podman network rm dnd_network 2>/dev/null || true
        echo "✅ Cleanup complete"
        ;;
    "help"|*)
        echo "D&D Character Creator - Podman Management Script"
        echo ""
        echo "Usage: $0 <command> [options]"
        echo ""
        echo "Commands:"
        echo "  setup     - Initial setup (create directories, .env file)"
        echo "  up        - Start all services"
        echo "  down      - Stop all services"  
        echo "  build     - Build the API image"
        echo "  logs      - Show service logs"
        echo "  status    - Show container/network/volume status"
        echo "  shell     - Open shell in container (api|db)"
        echo "  test      - Test API endpoints"
        echo "  clean     - Remove all containers, images, and volumes"
        echo "  help      - Show this help message"
        echo ""
        echo "Examples:"
        echo "  $0 setup           # Initial setup"
        echo "  $0 up              # Start services"
        echo "  $0 logs api        # Show API logs"
        echo "  $0 shell db        # Open database shell"
        echo "  $0 test            # Test API"
        ;;
esac
