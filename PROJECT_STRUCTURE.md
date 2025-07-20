# 📁 Project Structure

This document outlines the structure of the Context Engineering Multi-Agent Coffee System.

## 🏗️ **Core Directories**

### `/agents/`
Contains all AI agent implementations:
- `coffee_generator.py` - Main coffee code generation agent
- `quality_analyzer.py` - Code quality analysis agent  
- `optimizer.py` - Code optimization agent
- `user_proxy.py` - User interaction proxy agent
- `models.py` - Data models and schemas

### `/interfaces/`
User interface implementations:
- `chainlit_app.py` - Web interface using Chainlit
- `cli.py` - Command-line interface

### `/workflows/`
Multi-agent workflow orchestration:
- `coffee_workflow.py` - Main coffee generation workflow
- `cli_workflow.py` - CLI workflow implementation

### `/tools/`
Utility tools and functions:
- `coffee_calculations.py` - Coffee brewing calculations
- `code_analysis.py` - Code analysis utilities
- `code_optimization.py` - Code optimization utilities

### `/config/`
Configuration management:
- `settings.py` - Application settings and configuration

### `/tests/`
Comprehensive test suite:
- `agents/` - Agent-specific tests
- `tools/` - Tool function tests
- `workflows/` - Workflow integration tests
- `test_integration.py` - Full system integration tests

### `/examples/`
Example configurations and usage:
- Sample model configurations
- Example agent implementations

### `/PRPs/`
Project Requirement Prompts:
- System design documents
- Multi-agent system specifications
- Template files

### `/use-cases/`
Specific use case implementations:
- `mcp-server/` - MCP (Model Context Protocol) server implementation

## 📄 **Configuration Files**

- `model_config.yaml` - AI model configuration
- `requirements.txt` - Python dependencies
- `chainlit.md` - Chainlit interface documentation
- `.env.example` - Environment variables template
- `.gitignore` - Git ignore patterns

## 🚀 **Getting Started**

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Run web interface:**
   ```bash
   chainlit run interfaces/chainlit_app.py --port 8011
   ```

4. **Run CLI interface:**
   ```bash
   python interfaces/cli.py
   ```

## 🧪 **Testing**

Run the test suite:
```bash
pytest tests/
```

## 📚 **Documentation**

- `README.md` - English documentation
- `README-CN.md` - Chinese documentation  
- `API_SETUP.md` - API setup instructions
- `LICENSE` - Project license

## 🔧 **Development**

The project follows a modular architecture with clear separation of concerns:
- **Agents** handle specific AI tasks
- **Workflows** orchestrate multi-agent interactions
- **Interfaces** provide user interaction points
- **Tools** offer utility functions
- **Tests** ensure code quality and reliability

Each component is designed to be independently testable and maintainable.