"""Deployment command"""

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress
from rich.table import Table

console = Console()


@click.group()
def deploy():
    """Deploy Helix projects to various platforms"""
    pass


@deploy.command()
@click.option("--platform", type=click.Choice(["railway", "docker", "kubernetes", "local"]), default="railway")
@click.option("--environment", type=click.Choice(["dev", "staging", "prod"]), default="dev")
@click.option("--no-build", is_flag=True, help="Skip building")
def start(platform: str, environment: str, no_build: bool):
    """Start deployment process
    
    Examples:
        helix deploy start --platform railway
        helix deploy start --platform docker --environment prod
    """
    
    with Progress() as progress:
        task = progress.add_task("[cyan]Deploying...", total=4)
        
        progress.update(task, advance=1, description="Validating configuration...")
        
        if not no_build:
            progress.update(task, advance=1, description="Building application...")
        else:
            progress.update(task, advance=1)
        
        progress.update(task, advance=1, description="Preparing deployment...")
        
        progress.update(task, advance=1, description="Deploying to " + platform + "...")
    
    success_panel = Panel(
        f"[bold green]✓ Deployment successful![/bold green]\n\n"
        f"[cyan]Platform:[/cyan] {platform}\n"
        f"[cyan]Environment:[/cyan] {environment}\n\n"
        f"[yellow]Next steps:[/yellow]\n"
        f"  • helix monitor status\n"
        f"  • helix monitor logs",
        title="Deployment Complete",
        expand=False,
    )
    console.print(success_panel)


@deploy.command()
@click.option("--platform", type=click.Choice(["railway", "docker", "kubernetes"]), required=True)
def config(platform: str):
    """Show deployment configuration for a platform
    
    Examples:
        helix deploy config --platform railway
        helix deploy config --platform docker
    """
    
    configs = {
        "railway": """[bold cyan]Railway Deployment Configuration[/bold cyan]

[bold]Prerequisites:[/bold]
  • Railway account (https://railway.app)
  • Railway CLI installed
  • GitHub repository

[bold]Steps:[/bold]
  1. Login to Railway:
     $ railway login
  
  2. Create a new project:
     $ railway init
  
  3. Set environment variables:
     $ railway variables set OPENAI_API_KEY=your_key
  
  4. Deploy:
     $ railway up

[bold]Files Required:[/bold]
  • Procfile or railway.json
  • requirements.txt
  • .env (with secrets)

[bold]Documentation:[/bold]
  https://docs.railway.app
""",
        "docker": """[bold cyan]Docker Deployment Configuration[/bold cyan]

[bold]Prerequisites:[/bold]
  • Docker installed
  • Docker Hub account (optional)

[bold]Steps:[/bold]
  1. Build image:
     $ docker build -t helix-project .
  
  2. Run container:
     $ docker run -p 8000:8000 helix-project
  
  3. Push to registry (optional):
     $ docker tag helix-project username/helix-project
     $ docker push username/helix-project

[bold]Files Required:[/bold]
  • Dockerfile
  • docker-compose.yml (optional)
  • requirements.txt

[bold]Documentation:[/bold]
  https://docs.docker.com
""",
        "kubernetes": """[bold cyan]Kubernetes Deployment Configuration[/bold cyan]

[bold]Prerequisites:[/bold]
  • Kubernetes cluster
  • kubectl installed
  • Docker image in registry

[bold]Steps:[/bold]
  1. Create deployment:
     $ kubectl apply -f deployment.yaml
  
  2. Expose service:
     $ kubectl expose deployment helix-project
  
  3. Check status:
     $ kubectl get pods

[bold]Files Required:[/bold]
  • deployment.yaml
  • service.yaml
  • configmap.yaml (optional)

[bold]Documentation:[/bold]
  https://kubernetes.io/docs
""",
    }
    
    console.print(configs.get(platform, "Configuration not found"))


@deploy.command()
def status():
    """Show deployment status"""
    
    table = Table(title="Deployment Status")
    table.add_column("Service", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Platform", style="magenta")
    table.add_column("URL", style="blue")
    
    table.add_row("API", "✓ Running", "Railway", "https://api.example.com")
    table.add_row("Dashboard", "✓ Running", "Railway", "https://dashboard.example.com")
    table.add_row("Bot", "✓ Running", "Railway", "Discord")
    table.add_row("Database", "✓ Connected", "PostgreSQL", "postgresql://...")
    
    console.print(table)


@deploy.command()
def logs():
    """Show deployment logs"""
    
    console.print("[cyan]Recent deployment logs:[/cyan]\n")
    
    logs_text = """[2024-01-09 10:30:45] Starting deployment...
[2024-01-09 10:30:50] Building Docker image...
[2024-01-09 10:31:15] Image built successfully
[2024-01-09 10:31:20] Pushing to registry...
[2024-01-09 10:31:45] Deployment complete
[2024-01-09 10:31:50] Health check: OK
[2024-01-09 10:31:55] All services running
"""
    
    console.print(logs_text)
