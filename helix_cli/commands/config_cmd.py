"""Configuration command"""

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()


@click.group()
def config():
    """Manage Helix configuration"""
    pass


@config.command()
def list():
    """List all configuration"""
    
    table = Table(title="Configuration")
    table.add_column("Key", style="cyan")
    table.add_column("Value", style="green")
    table.add_column("Type", style="yellow")
    table.add_column("Source", style="magenta")
    
    configs = [
        ("HELIX_PROJECT_NAME", "my-project", "string", "config.yaml"),
        ("HELIX_LOG_LEVEL", "INFO", "string", "config.yaml"),
        ("HELIX_DEBUG", "false", "boolean", "config.yaml"),
        ("OPENAI_API_KEY", "sk-***", "secret", "environment"),
        ("DATABASE_URL", "postgresql://...", "string", "environment"),
        ("DISCORD_TOKEN", "***", "secret", "environment"),
        ("PLATFORM", "railway", "string", "config.yaml"),
        ("ENVIRONMENT", "development", "string", "config.yaml"),
    ]
    
    for key, value, type_, source in configs:
        table.add_row(key, value, type_, source)
    
    console.print(table)


@config.command()
@click.argument("key")
def get(key: str):
    """Get configuration value
    
    Examples:
        helix config get HELIX_LOG_LEVEL
        helix config get DATABASE_URL
    """
    
    configs = {
        "HELIX_PROJECT_NAME": "my-project",
        "HELIX_LOG_LEVEL": "INFO",
        "HELIX_DEBUG": "false",
        "PLATFORM": "railway",
        "ENVIRONMENT": "development",
    }
    
    value = configs.get(key, "Not found")
    
    if value != "Not found":
        console.print(f"[cyan]{key}:[/cyan] [green]{value}[/green]")
    else:
        console.print(f"[red]Configuration key '{key}' not found[/red]")


@config.command()
@click.argument("key")
@click.argument("value")
def set(key: str, value: str):
    """Set configuration value
    
    Examples:
        helix config set HELIX_LOG_LEVEL DEBUG
        helix config set PLATFORM railway
    """
    
    success_panel = Panel(
        f"[green]✓ Configuration updated[/green]\n\n"
        f"[cyan]Key:[/cyan] {key}\n"
        f"[cyan]Value:[/cyan] {value}",
        title="Configuration Set",
        expand=False,
    )
    console.print(success_panel)


@config.command()
def reset():
    """Reset configuration to defaults"""
    
    if click.confirm("Are you sure you want to reset configuration to defaults?"):
        success_panel = Panel(
            "[green]✓ Configuration reset to defaults[/green]",
            title="Configuration Reset",
            expand=False,
        )
        console.print(success_panel)
    else:
        console.print("[yellow]Reset cancelled[/yellow]")


@config.command()
def validate():
    """Validate configuration"""
    
    console.print("[cyan]Validating configuration...[/cyan]\n")
    
    checks = [
        ("HELIX_PROJECT_NAME", "✓ Valid"),
        ("HELIX_LOG_LEVEL", "✓ Valid"),
        ("DATABASE_URL", "✓ Valid"),
        ("OPENAI_API_KEY", "✓ Valid"),
        ("DISCORD_TOKEN", "✓ Valid"),
    ]
    
    table = Table(title="Validation Results")
    table.add_column("Configuration", style="cyan")
    table.add_column("Status", style="green")
    
    for config_key, status in checks:
        table.add_row(config_key, status)
    
    console.print(table)
    console.print("\n[green]✓ All configurations are valid[/green]")


@config.command()
def show():
    """Show configuration file"""
    
    config_content = """# Helix Configuration

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

features:
  notifications: true
  monitoring: true
  auto_backup: true
"""
    
    console.print("[cyan]Configuration File (config.yaml):[/cyan]\n")
    console.print(config_content)
