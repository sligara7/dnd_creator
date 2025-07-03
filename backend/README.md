# D&D Character Creator Backend

A FastAPI-based REST API for creating, managing, and evolving D&D 5e (2024) characters with AI assistance.

## 🏗️ Architecture

```
backend/
├── src/                      # Source code (modular structure)
│   ├── api/                  # API endpoints and routing
│   ├── core/                 # Core configuration and enums
│   ├── models/               # Data models and database schemas
│   └── services/             # Business logic and external services
├── data/                     # Database and persistent data
├── logs/                     # Application logs
├── characters/               # Character storage
├── custom_content/           # User-generated content
├── scripts/                  # Build and deployment scripts
├── tests/                    # Test suites
├── app.py                    # FastAPI application
├── main.py                   # Application entry point
└── requirements.txt          # Python dependencies
```

## 🚀 Quick Start

### Using Podman (Recommended)

1. **Setup Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

2. **Build and Run**
   ```bash
   ./scripts/build_and_run.sh
   ```

3. **Access the API**
   - API: http://localhost:8000
   - Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

### Using Docker Compose (Development)

1. **Setup Environment**
   ```bash
   cp .env.example .env
   ```

2. **Start Development Environment**
   ```bash
   docker-compose -f docker-compose.dev.yml up --build
   ```

3. **With PostgreSQL** (optional)
   ```bash
   docker-compose -f docker-compose.dev.yml --profile postgres up --build
   ```

### Local Development

1. **Setup Python Environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Setup Environment Variables**
   ```bash
   cp .env.example .env
   # Edit .env file
   ```

3. **Run the Application**
   ```bash
   python main.py
   # or
   uvicorn app:app --reload --host 0.0.0.0 --port 8000
   ```

## 🌟 Features

- **Character Creation**: AI-powered character generation from text prompts
- **Character Management**: Full CRUD operations for characters
- **Character Evolution**: Level up and modify existing characters
- **Custom Content**: Create and manage homebrew content
- **Validation**: Complete D&D 5e rule validation
- **Equipment System**: Weapons, armor, and magic items
- **Spellcasting**: Full spell management and casting
- **Real-time Gameplay**: Combat tracking, rest management, condition effects

## 📡 API Endpoints

### Core Endpoints
- `POST /api/v2/factory/create` - Create new content (characters, items, spells)
- `GET /api/v2/characters` - List all characters
- `POST /api/v2/characters` - Create a new character
- `GET /api/v2/characters/{id}` - Get character details
- `PUT /api/v2/characters/{id}` - Update character
- `DELETE /api/v2/characters/{id}` - Delete character

### Gameplay Endpoints
- `POST /api/v2/characters/{id}/level-up` - Level up character
- `POST /api/v2/characters/{id}/rest` - Take short/long rest
- `POST /api/v2/characters/{id}/combat` - Combat state management
- `GET /api/v2/characters/{id}/sheet` - Get formatted character sheet

### Validation & Tools
- `POST /api/v2/validate` - Validate character build
- `GET /api/v2/system/health` - Health check
- `GET /api/v2/system/metrics` - Performance metrics

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ENV` | Environment (development/production) | production |
| `DEBUG` | Enable debug mode | false |
| `HOST` | Server host | 0.0.0.0 |
| `PORT` | Server port | 8000 |
| `DATABASE_URL` | PostgreSQL URL (optional) | SQLite |
| `SQLITE_PATH` | SQLite database path | data/dnd_characters.db |
| `LLM_PROVIDER` | AI provider (openai/anthropic) | openai |
| `OPENAI_API_KEY` | OpenAI API key | - |
| `LLM_MODEL` | AI model to use | gpt-4.1-nano-2025-04-14 |

### Database Options

**SQLite (Default)**
- Zero configuration required
- Perfect for development and single-user deployments
- Database stored in `data/dnd_characters.db`

**PostgreSQL (Production)**
- Set `DATABASE_URL=postgresql://user:pass@host:5432/dbname`
- Better for multi-user production environments
- Supports advanced features and concurrent access

## 🔧 Development

### Project Structure
- **Core Models**: Character data structures and game mechanics
- **Services**: Business logic, AI integration, content generation
- **API Layer**: FastAPI endpoints and request/response handling
- **Database**: SQLAlchemy models and migrations

### Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src tests/

# Run specific test category
pytest tests/test_character_creation.py
```

### Code Quality
```bash
# Format code
black src/ tests/

# Lint code
flake8 src/ tests/

# Type checking
mypy src/
```

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**
   - Ensure `PYTHONPATH` includes both `/app` and `/app/src`
   - Check all import statements use the new modular structure

2. **Database Connection**
   - For SQLite: Ensure `data/` directory exists and is writable
   - For PostgreSQL: Verify connection string and database exists

3. **AI API Errors**
   - Check API keys are correctly set in `.env`
   - Verify rate limits aren't exceeded
   - Check network connectivity

4. **Container Issues**
   - Ensure volumes are properly mounted with `:Z` flag for SELinux
   - Check container logs: `podman logs dnd-backend-api`
   - Verify ports aren't already in use

### Performance Optimization

- **Caching**: AI responses are cached to reduce API calls
- **Rate Limiting**: Built-in rate limiting for AI providers
- **Database**: Use PostgreSQL for better concurrent performance
- **Monitoring**: Built-in metrics and health checks

## 📚 Documentation

- [API Documentation](http://localhost:8000/docs) - Interactive Swagger UI
- [ReDoc Documentation](http://localhost:8000/redoc) - Alternative API docs
- [Character Models](src/models/character_models.py) - Character data structures
- [Creation System](src/services/creation_factory.py) - Content creation logic

## 🤝 Contributing

1. Follow the modular architecture in `src/`
2. Add tests for new features
3. Update documentation for API changes
4. Use type hints and docstrings
5. Follow Python PEP 8 style guidelines

## 📄 License

[Add license information here]
