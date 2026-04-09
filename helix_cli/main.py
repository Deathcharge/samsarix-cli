#!/usr/bin/env python3
"""
Helix Collective CLI - Command-line interface for the Helix ecosystem
"""

import click
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from helix_cli.commands import (
    init_cmd,
    deploy_cmd,
    monitor_cmd,
    config_cmd,
    project_cmd,
)

console = Console()


@click.group()
@click.version_option(version="1.0.0", prog_name="helix")
def cli():
    """🧬 Helix Collective - AI Agent Orchestration Ecosystem CLI
    
    A comprehensive command-line interface for managing the entire Helix ecosystem.
    
    Examples:
        helix init my-project          # Initialize a new project
        helix deploy --platform railway # Deploy to Railway
        helix monitor status            # Check system status
        helix config list              # List configuration
    """
    pass


# Add command groups
cli.add_command(init_cmd.init, name="init")
cli.add_command(deploy_cmd.deploy, name="deploy")
cli.add_command(monitor_cmd.monitor, name="monitor")
cli.add_command(config_cmd.config, name="config")
cli.add_command(project_cmd.project, name="project")


@cli.command()
def version():
    """Show version information"""
    panel = Panel(
        Text("Helix Collective CLI v1.0.0", style="bold cyan"),
        title="Version Info",
        expand=False,
    )
    console.print(panel)


@cli.command()
def info():
    """Show ecosystem information"""
    info_text = """
[bold cyan]Helix Collective Ecosystem[/bold cyan]

[bold]14 Specialized Packages:[/bold]
  • agent-consensus - Multi-agent consensus
  • helix-chat-engine - Real-time chat
  • helix-integration - API integration
  • helix-notifications - Multi-channel notifications
  • helix-token-cost-manager - Cost tracking
  • neural-mesh - Distributed neural network
  • policy-engine - Policy enforcement
  • routine-engine - Task scheduling
  • unified-llm - LLM abstraction
  • helix-discord-bot - Discord bot
  • helix-agent-orchestration - Agent orchestration
  • helix-sdk - Unified Python SDK
  • helix-collective-dashboard - Monitoring dashboard
  • helix-website - Marketing website

[bold]Statistics:[/bold]
  • 388,476+ lines of production code
  • 24 specialized AI agents
  • Real-time monitoring
  • PyPI publishing ready
  • Docker & Kubernetes support

[bold]Quick Links:[/bold]
  • GitHub: https://github.com/Deathcharge
  • PyPI: https://pypi.org
  • Dashboard: https://github.com/Deathcharge/helix-collective-dashboard
"""
    console.print(info_text)


@cli.command()
def help_extended():
    """Show extended help and examples"""
    help_text = """
[bold cyan]Helix CLI - Extended Help[/bold cyan]

[bold]Project Commands:[/bold]
  helix init <name>              Initialize a new project
  helix project list             List all projects
  helix project status           Show project status
  helix project delete <name>    Delete a project

[bold]Deployment Commands:[/bold]
  helix deploy --platform railway    Deploy to Railway
  helix deploy --platform docker     Deploy with Docker
  helix deploy --platform kubernetes Deploy to Kubernetes
  helix deploy --local               Deploy locally

[bold]Monitoring Commands:[/bold]
  helix monitor status           System status
  helix monitor logs             View logs
  helix monitor metrics          Show metrics
  helix monitor health           Health check

[bold]Configuration Commands:[/bold]
  helix config list              List all config
  helix config get <key>         Get config value
  helix config set <key> <value> Set config value
  helix config reset             Reset to defaults

[bold]Examples:[/bold]
  # Create a new project
  $ helix init my-ai-project
  $ cd my-ai-project
  
  # Install dependencies
  $ pip install helix-collective
  
  # Deploy to Railway
  $ helix deploy --platform railway
  
  # Monitor the deployment
  $ helix monitor status
  $ helix monitor logs
  
  # Check configuration
  $ helix config list
  $ helix config set LOG_LEVEL debug

[bold]Documentation:[/bold]
  Run 'helix --help' for command help
  Run 'helix <command> --help' for command-specific help
  Visit https://github.com/Deathcharge for full documentation
"""
    console.print(help_text)


if __name__ == "__main__":
    cli()
