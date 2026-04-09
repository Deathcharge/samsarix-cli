"""Project initialization command"""

import os
import click
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress

console = Console()


@click.command()
@click.argument("project_name")
@click.option(
    "--template",
    type=click.Choice(["fastapi", "flask", "streamlit", "discord"]),
    default="fastapi",
    help="Project template to use",
)
@click.option("--no-git", is_flag=True, help="Skip git initialization")
def init(project_name: str, template: str, no_git: bool):
    """Initialize a new Helix project
    
    Creates a new project directory with the specified template.
    
    Examples:
        helix init my-project
        helix init my-project --template fastapi
        helix init my-project --template discord --no-git
    """
    
    project_path = Path(project_name)
    
    # Check if directory exists
    if project_path.exists():
        console.print(f"[red]Error: Directory '{project_name}' already exists[/red]")
        raise click.Abort()
    
    # Create project directory
    with Progress() as progress:
        task = progress.add_task("[cyan]Initializing project...", total=5)
        
        # Create directory structure
        progress.update(task, advance=1, description="Creating directories...")
        project_path.mkdir(parents=True)
        (project_path / "src").mkdir()
        (project_path / "tests").mkdir()
        (project_path / "docs").mkdir()
        (project_path / "config").mkdir()
        
        # Create files based on template
        progress.update(task, advance=1, description="Creating template files...")
        _create_template_files(project_path, template)
        
        # Create configuration
        progress.update(task, advance=1, description="Creating configuration...")
        _create_config_files(project_path, project_name)
        
        # Initialize git
        progress.update(task, advance=1, description="Initializing git...")
        if not no_git:
            _init_git(project_path)
        
        progress.update(task, advance=1, description="Done!")
    
    # Show success message
    success_panel = Panel(
        f"[bold green]✓ Project '{project_name}' created successfully![/bold green]\n\n"
        f"[cyan]Next steps:[/cyan]\n"
        f"  1. cd {project_name}\n"
        f"  2. pip install helix-collective\n"
        f"  3. helix project status\n"
        f"  4. helix deploy --platform railway",
        title="Project Created",
        expand=False,
    )
    console.print(success_panel)


def _create_template_files(project_path: Path, template: str):
    """Create template-specific files"""
    
    if template == "fastapi":
        _create_fastapi_template(project_path)
    elif template == "flask":
        _create_flask_template(project_path)
    elif template == "streamlit":
        _create_streamlit_template(project_path)
    elif template == "discord":
        _create_discord_template(project_path)


def _create_fastapi_template(project_path: Path):
    """Create FastAPI project template"""
    
    main_py = """from fastapi import FastAPI
from helix import Orchestrator, LLM

app = FastAPI(title="Helix Project")

# Initialize Helix components
orchestrator = Orchestrator()
llm = LLM(model="gpt-4")


@app.get("/")
async def root():
    return {"message": "Welcome to your Helix project!"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.post("/agent/run")
async def run_agent(prompt: str):
    # Your agent logic here
    response = await llm.generate(prompt)
    return {"response": response}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
"""
    
    (project_path / "src" / "main.py").write_text(main_py)
    
    requirements = """fastapi==0.104.1
uvicorn==0.24.0
helix-collective>=1.0.0
python-dotenv==1.0.0
"""
    (project_path / "requirements.txt").write_text(requirements)


def _create_flask_template(project_path: Path):
    """Create Flask project template"""
    
    main_py = """from flask import Flask, jsonify, request
from helix import Orchestrator, LLM

app = Flask(__name__)

# Initialize Helix components
orchestrator = Orchestrator()
llm = LLM(model="gpt-4")


@app.route("/")
def root():
    return jsonify({"message": "Welcome to your Helix project!"})


@app.route("/health")
def health():
    return jsonify({"status": "healthy"})


@app.route("/agent/run", methods=["POST"])
def run_agent():
    data = request.get_json()
    prompt = data.get("prompt", "")
    
    # Your agent logic here
    response = llm.generate(prompt)
    return jsonify({"response": response})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
"""
    
    (project_path / "src" / "main.py").write_text(main_py)
    
    requirements = """Flask==3.0.0
helix-collective>=1.0.0
python-dotenv==1.0.0
"""
    (project_path / "requirements.txt").write_text(requirements)


def _create_streamlit_template(project_path: Path):
    """Create Streamlit project template"""
    
    app_py = """import streamlit as st
from helix import Orchestrator, LLM

st.set_page_config(page_title="Helix Project", layout="wide")

st.title("🧬 Helix Collective Project")

# Initialize Helix components
orchestrator = Orchestrator()
llm = LLM(model="gpt-4")

# Sidebar
with st.sidebar:
    st.header("Configuration")
    model = st.selectbox("Select Model", ["gpt-4", "gpt-3.5-turbo"])
    temperature = st.slider("Temperature", 0.0, 1.0, 0.7)

# Main content
st.header("AI Agent Interface")

prompt = st.text_area("Enter your prompt:", height=100)

if st.button("Run Agent", type="primary"):
    with st.spinner("Processing..."):
        response = llm.generate(prompt, temperature=temperature)
        st.success("Done!")
        st.write(response)

# Display metrics
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Agents Active", 24)
with col2:
    st.metric("Tokens Used", "1,234")
with col3:
    st.metric("Cost", "$0.05")
"""
    
    (project_path / "src" / "app.py").write_text(app_py)
    
    requirements = """streamlit==1.28.0
helix-collective>=1.0.0
python-dotenv==1.0.0
"""
    (project_path / "requirements.txt").write_text(requirements)


def _create_discord_template(project_path: Path):
    """Create Discord bot project template"""
    
    bot_py = """import discord
from discord.ext import commands
from helix import Orchestrator, LLM

# Initialize bot
bot = commands.Bot(command_prefix="!", intents=discord.Intents.default())

# Initialize Helix components
orchestrator = Orchestrator()
llm = LLM(model="gpt-4")


@bot.event
async def on_ready():
    print(f"{bot.user} has connected to Discord!")


@bot.command(name="hello")
async def hello(ctx):
    await ctx.send(f"Hello {ctx.author.name}!")


@bot.command(name="agent")
async def agent(ctx, *, prompt):
    async with ctx.typing():
        response = await llm.generate(prompt)
        await ctx.send(response)


@bot.command(name="status")
async def status(ctx):
    agents = orchestrator.get_agents()
    await ctx.send(f"Active agents: {len(agents)}")


if __name__ == "__main__":
    bot.run("YOUR_DISCORD_TOKEN")
"""
    
    (project_path / "src" / "bot.py").write_text(bot_py)
    
    requirements = """discord.py==2.3.2
helix-collective>=1.0.0
python-dotenv==1.0.0
"""
    (project_path / "requirements.txt").write_text(requirements)


def _create_config_files(project_path: Path, project_name: str):
    """Create configuration files"""
    
    # .env.example
    env_example = """# Helix Configuration
HELIX_PROJECT_NAME={project_name}
HELIX_LOG_LEVEL=INFO
HELIX_DEBUG=false

# API Keys
OPENAI_API_KEY=your_key_here
DISCORD_TOKEN=your_token_here

# Database
DATABASE_URL=sqlite:///helix.db

# Deployment
PLATFORM=local
ENVIRONMENT=development
""".format(project_name=project_name)
    
    (project_path / ".env.example").write_text(env_example)
    
    # .gitignore
    gitignore = """# Environment
.env
.env.local
.env.*.local

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
ENV/
env/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Project
.helix/
logs/
*.log
"""
    
    (project_path / ".gitignore").write_text(gitignore)
    
    # README.md
    readme = f"""# {project_name}

A Helix Collective project.

## Getting Started

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure environment:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

3. Run the project:
   ```bash
   python src/main.py
   ```

## Deployment

Deploy to Railway:
```bash
helix deploy --platform railway
```

## Documentation

- [Helix Collective](https://github.com/Deathcharge)
- [Helix SDK](https://github.com/Deathcharge/helix-sdk)
- [Dashboard](https://github.com/Deathcharge/helix-collective-dashboard)

## License

Apache 2.0 & Proprietary
"""
    
    (project_path / "README.md").write_text(readme)


def _init_git(project_path: Path):
    """Initialize git repository"""
    
    os.chdir(project_path)
    os.system("git init > /dev/null 2>&1")
    os.system("git config user.email 'helix@local' > /dev/null 2>&1")
    os.system("git config user.name 'Helix' > /dev/null 2>&1")
    os.system("git add . > /dev/null 2>&1")
    os.system("git commit -m 'Initial commit' > /dev/null 2>&1")
