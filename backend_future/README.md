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

The updated D&D 2024 core rules will be released under a Creative Commons Attribution 4.0 International (CC-BY-4.0) license. This license allows third-party creators to use, adapt, and publish content based on the rules, provided they give appropriate attribution to Michael Best & Friedrich LLP. This is a significant change from the previous Open Game License (OGL), and is intended to foster a more open and collaborative environment for third-party content creation. 
Here's a more detailed breakdown:
Creative Commons Attribution 4.0 (CC-BY-4.0):
This license is a globally recognized standard that allows for broad use of the licensed material with minimal restrictions. The key requirement is that users must give appropriate credit to the original creator of D&D Beyond. 
SRD 5.2:
The updated System Reference Document (SRD), version 5.2, will incorporate the 2024 core rules and be released under the CC-BY-4.0 license. This document provides the foundational rules content that third-party creators can use for their products. 
No OGL:
Unlike the previous SRD 5.1, the new SRD 5.2 will not be released under the OGL. Instead, it will be exclusively under the CC-BY-4.0 license. 
Irrevocable License:
The Creative Commons license is irrevocable, meaning that once it's granted, it cannot be taken back. 
Community Feedback:
The decision to use Creative Commons for the 2024 rules was influenced by community feedback following the OGL controversy.

## 📄 License

This project is licensed under the Creative Commons Attribution 4.0 International (CC BY 4.0) license. See the LICENSE file for details.

- D&D 2024 Core Rules and SRD 5.2: © Wizards of the Coast, published under CC-BY-4.0
- This project: © 2025 [Anthony James Sligar]

You are free to share and adapt the material for any purpose, even commercially, as long as you provide appropriate attribution. For more information, see https://creativecommons.org/licenses/by/4.0/

