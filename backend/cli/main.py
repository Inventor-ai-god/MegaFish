"""MegaFish CLI — entry point."""

import sys
from pathlib import Path

import typer

from . import installer, launcher
from . import ui
from .client import (
    build_graph,
    create_project,
    create_simulation,
    get_result_url,
    poll_simulation,
    poll_task,
    upload_file,
)

app = typer.Typer(
    add_completion=False,
    help="MegaFish — multi-agent swarm intelligence engine",
    invoke_without_command=True,
)


@app.callback()
def _default(ctx: typer.Context, prompt: str = typer.Argument(None)):
    """Run MegaFish: simulate public reaction to any scenario."""
    if ctx.invoked_subcommand is not None:
        return
    try:
        if not installer.is_installed():
            installer.run_install()
        ui.splash()
        ui.info_panel()
        if not prompt:
            prompt = ui.prompt_box()
        file_path = ui.ask_file()
        ui.console.print()
        launcher.ensure_services()
        ui.console.print()
        with ui.progress("Running simulation...") as prog:
            task = prog.add_task("sim")
            try:
                result_url = _run_simulation(prompt, file_path)
            finally:
                prog.update(task, completed=100)
        ui.success(f"Done → {result_url}")
        launcher.open_browser(result_url)
    except KeyboardInterrupt:
        ui.console.print("\n[red]  Exiting MegaFish.[/red]")
        raise SystemExit(0)


def _run_simulation(prompt: str, file_path: str | None) -> str:
    """Create project, optionally upload file, build graph, run simulation. Returns result URL."""
    ui.status("Creating project...")
    project = create_project(prompt[:80])
    project_id = project.get("id") or project.get("project_id") or project["data"]["id"]

    if file_path:
        ui.status(f"Uploading {file_path}...")
        upload_file(project_id, file_path)

    ui.status("Building knowledge graph...")
    task = build_graph(project_id)
    task_id = task.get("task_id") or task.get("id")
    if task_id:
        poll_task(task_id, on_progress=lambda m: ui.status(f"Graph: {m}"))

    ui.status("Generating agents and running simulation...")
    sim = create_simulation(project_id)
    sim_id = sim.get("id") or sim.get("simulation_id") or sim["data"]["id"]
    poll_simulation(sim_id, on_progress=lambda m: ui.status(f"Sim: {m}"))

    port = launcher.check_frontend() or 3000
    return get_result_url(sim_id, port)



@app.command()
def install():
    """Run the MegaFish install wizard."""
    installer.run_install()


@app.command()
def update():
    """Pull the latest MegaFish version from GitHub."""
    installer.run_update()


@app.command()
def uninstall():
    """Uninstall MegaFish and remove all associated data."""
    installer.run_uninstall()


@app.command()
def status():
    """Show status of all MegaFish services."""
    ui.splash()
    neo4j = launcher.check_neo4j()
    ollama = launcher.check_ollama()
    backend = launcher.check_backend()
    frontend = launcher.check_frontend()
    ui.success("Neo4j") if neo4j else ui.error("Neo4j not running")
    ui.success("Ollama") if ollama else ui.error("Ollama not running")
    ui.success("Backend") if backend else ui.error("Backend not running")
    ui.success(f"Frontend → http://localhost:{frontend}") if frontend else ui.error("Frontend not running")


@app.command()
def stop():
    """Stop all MegaFish services started by this CLI."""
    launcher.stop_all()
    ui.success("All MegaFish services stopped.")


@app.command(name="help")
def help_cmd():
    """Show MegaFish commands, usage, and info."""
    ui.splash()
    ui.console.print("  [bold red]Commands[/bold red]\n")
    ui.console.print("    [red]megafish[/red]                   Run a simulation (interactive prompt)")
    ui.console.print("    [red]megafish[/red] [dim]\"your scenario\"[/dim]  Run a simulation directly")
    ui.console.print("    [red]megafish update[/red]            Pull the latest version from GitHub")
    ui.console.print("    [red]megafish status[/red]            Show Neo4j / Ollama / backend / frontend status")
    ui.console.print("    [red]megafish stop[/red]              Stop all services started by MegaFish")
    ui.console.print("    [red]megafish uninstall[/red]         Uninstall MegaFish")
    ui.console.print("    [red]megafish help[/red]              Show this help\n")
    ui.console.print("  [bold red]Examples[/bold red]\n")
    ui.console.print('    megafish [dim]"Apple announces $500 iPhone"[/dim]')
    ui.console.print('    megafish [dim]"NATO expands to include Ukraine"[/dim]')
    ui.console.print('    megafish [dim]"New climate legislation passes"[/dim]\n')
    ui.console.print("  [bold red]How it works[/bold red]\n")
    ui.console.print("    1. Builds a knowledge graph from your scenario (+ optional file)")
    ui.console.print("    2. Generates AI agent personas across demographics")
    ui.console.print("    3. Runs a social media simulation (Twitter / Reddit)")
    ui.console.print("    4. Opens results in your browser at localhost:3000\n")
    ui.console.print("  [red]v0.2.0  ·  AGPL-3.0  ·  Offline  ·  Local[/red]\n")


if __name__ == "__main__":
    app()
