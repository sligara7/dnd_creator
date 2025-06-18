# D&D Character Creator Backend

A sophisticated D&D 5e character creation system powered by OpenAI's GPT-4.1-nano for creative content generation.

## 🔐 Security Setup

### GitHub Secrets Configuration

This project uses GitHub Secrets to securely manage API keys. **Never commit API keys to your repository.**

#### Required GitHub Secrets

Set up these secrets in your repository:
1. Go to your repository → Settings → Secrets and variables → Actions
2. Click "New repository secret" and add:

- `OPENAI_API_KEY` - Your OpenAI API key (starts with `-...`)
- `ANTHROPIC_API_KEY` - Your Anthropic API key (optional)  
- `DB_PASSWORD` - PostgreSQL database password
- `SECRET_KEY` - Application secret key

### Local Development Setup

1. **Run the setup script**
   ```bash
   ./setup-dev.sh
   ```

2. **Configure environment variables**
   ```bash
   # Edit .env file with your API keys
   nano .env
   ```

3. **Test the setup**
   ```bash
   python test_llm_diagnostic.py
   ```

## 🚀 Quick Start

### Development Mode

```bash
# CLI interface
python main.py cli

# HTTP server  
python main.py server 8000

# Validation demo
python main.py validate
```

### Production Deployment with Podman

```bash
# Using environment variables from GitHub secrets
OPENAI_API_KEY=${{ secrets.OPENAI_API_KEY }} podman-compose up -d
```

## 🧪 Testing

### Basic Tests
```bash
python test_llm_diagnostic.py      # Full diagnostic
python test_openai.py             # OpenAI integration  
python test_character_openai.py   # Character creation
```

### Creative Stress Test
```bash
python test_creative.py           # Test custom content generation
```

## 🔧 Key Features

- ✅ **OpenAI GPT-4.1-nano integration** - Fast, cost-effective AI generation
- ✅ **Secure API key management** - GitHub secrets + Docker/Podman secrets
- ✅ **Creative content generation** - Custom classes, species, items, spells
- ✅ **RESTful API** - Clean HTTP endpoints for web integration
- ✅ **Comprehensive validation** - D&D 5e rule compliance checking
- ✅ **Multiple output formats** - JSON, formatted text, character sheets
- ✅ **Container deployment** - Podman/Docker ready with health checks

