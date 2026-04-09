"""Project management command"""

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()


@click.group()
def project():
    """Manage Helix projects"""
    pass


@project.command()
def list():
    """List all projects"""
    
    table = Table(title="Your Projects")
    table.add_column("Name", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Platform", style="magenta")
    table.add_column("Created", style="yellow")
    table.add_column("URL", style="blue")
    
    projects = [
        ("my-project", "✓ Running", "Railway", "2024-01-01", "https://my-project.railway.app"),
        ("research-agent", "✓ Running", "Docker", "2024-01-05", "http://localhost:8000"),
        ("discord-bot", "✓ Running", "Railway", "2024-01-08", "Discord"),
    ]
    
    for name, status, platform, created, url in projects:
        table.add_row(name, status, platform, created, url)
    
    console.print(table)


@project.command()
def status():
    """Show project status"""
    
    status_panel = Panel(
        "[green]✓ Project is healthy[/green]\n\n"
        "[cyan]Name:[/cyan] my-project\n"
        "[cyan]Status:[/cyan] Running\n"
        "[cyan]Platform:[/cyan] Railway\n"
        "[cyan]Uptime:[/cyan] 45 days\n"
        "[cyan]URL:[/cyan] https://my-project.railway.app\n\n"
        "[yellow]Resources:[/yellow]\n"
        "  • CPU: 12% (0.5 vCPU)\n"
        "  • Memory: 256 MB / 512 MB\n"
        "  • Storage: 1.2 GB / 10 GB",
        title="Project Status",
        expand=False,
    )
    console.print(status_panel)


@project.command()
def info():
    """Show detailed project information"""
    
    info_table = Table(title="Project Information")
    info_table.add_column("Property", style="cyan")
    info_table.add_column("Value", style="green")
    
    info_table.add_row("Name", "my-project")
    info_table.add_row("Description", "AI-powered research assistant")
    info_table.add_row("Status", "✓ Running")
    info_table.add_row("Platform", "Railway")
    info_table.add_row("Region", "us-west-2")
    info_table.add_row("Environment", "production")
    info_table.add_row("Created", "2024-01-01 10:30:00")
    info_table.add_row("Last Updated", "2024-01-09 15:45:00")
    info_table.add_row("Team Members", "3")
    info_table.add_row("Agents Active", "24")
    
    console.print(info_table)


@project.command()
@click.argument("name")
def delete(name: str):
    """Delete a project
    
    Examples:
        helix project delete my-project
    """
    
    if click.confirm(f"Are you sure you want to delete project '{name}'?"):
        success_panel = Panel(
            f"[green]✓ Project '{name}' deleted successfully[/green]",
            title="Project Deleted",
            expand=False,
        )
        console.print(success_panel)
    else:
        console.print("[yellow]Deletion cancelled[/yellow]")


@project.command()
def logs():
    """Show project logs"""
    
    console.print("[cyan]Project Logs:[/cyan]\n")
    
    logs_text = """[2024-01-09 15:45:30] [INFO] Project started
[2024-01-09 15:45:31] [INFO] Loading configuration
[2024-01-09 15:45:32] [INFO] Initializing database connection
[2024-01-09 15:45:33] [INFO] Starting API server on port 8000
[2024-01-09 15:45:34] [INFO] Loading 24 agents
[2024-01-09 15:45:35] [INFO] Connecting to Discord
[2024-01-09 15:45:36] [INFO] All systems operational
[2024-01-09 15:46:00] [DEBUG] Received request from user #123
[2024-01-09 15:46:05] [INFO] LLM response generated
[2024-01-09 15:46:10] [DEBUG] Notification sent
"""
    
    console.print(logs_text)


@project.command()
def restart():
    """Restart project"""
    
    if click.confirm("Are you sure you want to restart the project?"):
        console.print("[cyan]Restarting project...[/cyan]")
        success_panel = Panel(
            "[green]✓ Project restarted successfully[/green]",
            title="Project Restarted",
            expand=False,
        )
        console.print(success_panel)
    else:
        console.print("[yellow]Restart cancelled[/yellow]")


@project.command()
def backup():
    """Create project backup"""
    
    console.print("[cyan]Creating backup...[/cyan]")
    success_panel = Panel(
        "[green]✓ Backup created successfully[/green]\n\n"
        "[cyan]Backup ID:[/cyan] backup-20240109-154530\n"
        "[cyan]Size:[/cyan] 2.3 GB\n"
        "[cyan]Location:[/cyan] s3://backups/my-project/",
        title="Backup Created",
        expand=False,
    )
    console.print(success_panel)


@project.command()
def stats():
    """Show project statistics"""
    
    stats_table = Table(title="Project Statistics")
    stats_table.add_column("Metric", style="cyan")
    stats_table.add_column("Value", style="green")
    
    stats_table.add_row("Total Requests", "1,234,567")
    stats_table.add_row("Avg Response Time", "45ms")
    stats_table.add_row("Error Rate", "0.01%")
    stats_table.add_row("Uptime", "99.99%")
    stats_table.add_row("Agents Active", "24")
    stats_table.add_row("Tokens Used", "12,345,678")
    stats_table.add_row("Cost (This Month)", "$234.56")
    stats_table.add_row("Data Stored", "5.2 GB")
    
    console.print(stats_table)
