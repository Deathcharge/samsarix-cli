# Helix CLI - Command-Line Interface for the Helix Collective

A comprehensive, user-friendly command-line interface for managing the entire Helix Collective ecosystem.

## Features

✨ **Project Management**
- Initialize new projects with templates
- Manage multiple projects
- View project status and statistics

🚀 **Deployment**
- Deploy to Railway, Docker, Kubernetes
- Multiple environment support (dev, staging, prod)
- Automated build and deployment

📊 **Monitoring**
- Real-time system status
- Performance metrics
- Health checks
- Alert management

⚙️ **Configuration**
- Centralized configuration management
- Environment variable handling
- Configuration validation

## Installation

### From PyPI
```bash
pip install helix-cli
```

### From Source
```bash
git clone https://github.com/Deathcharge/helix-cli.git
cd helix-cli
pip install -e .
```

## Quick Start

### 1. Initialize a New Project
```bash
helix init my-project --template fastapi
cd my-project
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment
```bash
cp .env.example .env
# Edit .env with your settings
```

### 4. Deploy
```bash
helix deploy --platform railway
```

### 5. Monitor
```bash
helix monitor status
helix monitor logs
```

## Commands

### Project Management

```bash
# Initialize a new project
helix init <name> [--template TEMPLATE] [--no-git]

# List all projects
helix project list

# Show project status
helix project status

# Show detailed project information
helix project info

# Delete a project
helix project delete <name>

# View project logs
helix project logs

# Restart a project
helix project restart

# Create a backup
helix project backup

# Show project statistics
helix project stats
```

### Deployment

```bash
# Start deployment
helix deploy start [--platform PLATFORM] [--environment ENV] [--no-build]

# Show deployment configuration
helix deploy config --platform PLATFORM

# Show deployment status
helix deploy status

# View deployment logs
helix deploy logs
```

### Monitoring

```bash
# Show system status
helix monitor status

# View recent logs
helix monitor logs [--lines N]

# Show performance metrics
helix monitor metrics

# Run health checks
helix monitor health

# Show active alerts
helix monitor alerts
```

### Configuration

```bash
# List all configuration
helix config list

# Get a configuration value
helix config get <key>

# Set a configuration value
helix config set <key> <value>

# Reset configuration to defaults
helix config reset

# Validate configuration
helix config validate

# Show configuration file
helix config show
```

### Utility

```bash
# Show version
helix --version

# Show help
helix --help

# Show ecosystem information
helix info

# Show extended help
helix help-extended
```

## Templates

The CLI supports multiple project templates:

### FastAPI
Modern async Python web framework
```bash
helix init my-project --template fastapi
```

### Flask
Lightweight Python web framework
```bash
helix init my-project --template flask
```

### Streamlit
Data science and ML web app framework
```bash
helix init my-project --template streamlit
```

### Discord Bot
Discord bot with Helix integration
```bash
helix init my-project --template discord
```

## Deployment Platforms

### Railway
Cloud platform for deploying applications
```bash
helix deploy start --platform railway
```

### Docker
Containerized deployment
```bash
helix deploy start --platform docker
```

### Kubernetes
Orchestrated container deployment
```bash
helix deploy start --platform kubernetes
```

### Local
Local development deployment
```bash
helix deploy start --platform local
```

## Configuration

### Environment Variables

Create a `.env` file in your project:

```env
# Helix Configuration
HELIX_PROJECT_NAME=my-project
HELIX_LOG_LEVEL=INFO
HELIX_DEBUG=false

# API Keys
OPENAI_API_KEY=your_key_here
DISCORD_TOKEN=your_token_here

# Database
DATABASE_URL=postgresql://user:pass@localhost/db

# Deployment
PLATFORM=railway
ENVIRONMENT=development
```

### Configuration File

Create a `config.yaml` in your project:

```yaml
project:
  name: my-project
  environment: development
  debug: false

logging:
  level: INFO
  format: json
  output: console

deployment:
  platform: railway
  region: us-west-2
  auto_scaling: true

services:
  api:
    port: 8000
    workers: 4
  database:
    type: postgresql
    pool_size: 10
  cache:
    type: redis
    ttl: 3600
```

## Examples

### Create a FastAPI Project
```bash
helix init my-api --template fastapi
cd my-api
pip install -r requirements.txt
python src/main.py
```

### Create a Discord Bot
```bash
helix init my-bot --template discord
cd my-bot
pip install -r requirements.txt
# Set DISCORD_TOKEN in .env
python src/bot.py
```

### Deploy to Railway
```bash
helix init my-project --template fastapi
cd my-project
helix deploy start --platform railway
helix monitor status
```

### Monitor Your Application
```bash
helix monitor status
helix monitor logs --lines 50
helix monitor metrics
helix monitor health
```

## Troubleshooting

### Command Not Found
Make sure the CLI is installed:
```bash
pip install helix-cli
```

### Configuration Issues
Validate your configuration:
```bash
helix config validate
```

### Deployment Failures
Check deployment logs:
```bash
helix deploy logs
```

### Health Check Failures
Run a full health check:
```bash
helix monitor health
```

## Development

### Install Development Dependencies
```bash
pip install -e ".[dev]"
```

### Run Tests
```bash
pytest tests/
```

### Code Quality
```bash
black helix_cli/
flake8 helix_cli/
mypy helix_cli/
```

## Contributing

Contributions are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md).

## License

Apache License 2.0 & Proprietary

See [LICENSE](LICENSE) and [LICENSE.PROPRIETARY](LICENSE.PROPRIETARY) for details.

## Support

- 📖 [Documentation](https://github.com/Deathcharge/helix-cli)
- 🐛 [Issue Tracker](https://github.com/Deathcharge/helix-cli/issues)
- 💬 [Discussions](https://github.com/Deathcharge/helix-cli/discussions)

## Ecosystem

The Helix CLI is part of the Helix Collective ecosystem:

- [helix-sdk](https://github.com/Deathcharge/helix-sdk) - Unified Python SDK
- [helix-agent-orchestration](https://github.com/Deathcharge/helix-agent-orchestration) - Agent orchestration
- [helix-collective-dashboard](https://github.com/Deathcharge/helix-collective-dashboard) - Monitoring dashboard
- [helix-website](https://github.com/Deathcharge/helix-website) - Marketing website

## Changelog

### v1.0.0 (2024-01-09)
- Initial release
- Project management commands
- Deployment commands
- Monitoring commands
- Configuration management
- Multiple project templates
- Multi-platform deployment support

---

Made with ❤️ by the Helix Collective
