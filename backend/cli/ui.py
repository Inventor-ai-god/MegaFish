"""MegaFish CLI — terminal UI (red theme)."""

from rich.console import Console
from rich.theme import Theme
from rich.panel import Panel
from rich.prompt import Prompt
import sys

err_console = Console(stderr=True, theme=Theme({"default": "bold red"}))

FISH_ART = r"""
                          .
                          A       ;
                |   ,--,-/ \---,-/|  ,
               _|\,'. /|      /|   `/|-.
           \`.'    /|      ,            `;.
          ,'\   A     A         A   A _ /| `.;
        ,/  _              A       _  / _   /|  ;
       /\  / \   ,  ,           A  /    /     `/|
      /_| | _ \         ,     ,             ,/  \
     // | |/ `.\  ,-      ,       ,   ,/ ,/      \/
     / @| |@  / /'   \  \      ,              >  /|    ,--.
    |\_/   \_/ /      |  |           ,  ,/        \  ./' __:..
    |  __ __  |       |  | .--.  ,         >  >   |-'   /     `
  ,/| /  '  \ |       |  |     \      ,           |    /
 /  |<--.__,->|       |  | .    `.        >  >    /   (
/_,' \\  ^  /  \     /  /   `.    >--            /^\   |
      \\___/    \   /  /      \__'     \   \   \/   \  |
       `.   |/          ,  ,                  /`\    \  )
         \  '  |/    ,       V    \          /        `-\
          `|/  '  V      V           \    \.'            \_
           '`-.       V       V        \./'\
               `|/-.      \ /   \ /,---`\
                /   `._____V_____V'
                           '     '
"""

LOGO_TEXT = r"""
███╗   ███╗███████╗ ██████╗  █████╗ ███████╗██╗███████╗██╗  ██╗
████╗ ████║██╔════╝██╔════╝ ██╔══██╗██╔════╝██║██╔════╝██║  ██║
██╔████╔██║█████╗  ██║  ███╗███████║█████╗  ██║███████╗███████║
██║╚██╔╝██║██╔══╝  ██║   ██║██╔══██║██╔══╝  ██║╚════██║██╔══██║
██║ ╚═╝ ██║███████╗╚██████╔╝██║  ██║██║     ██║███████║██║  ██║
╚═╝     ╚═╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝
"""

console = Console(theme=Theme({"default": "bold red"}))


def splash():
    console.clear()
    console.print(FISH_ART, style="bold red")
    console.print(LOGO_TEXT, style="bold red")
    console.print("  v0.2.0  —  Multi-agent swarm intelligence engine", style="red")
    console.print("─" * 66, style="red")
    console.print()


def info_panel():
    from rich.table import Table
    from rich.columns import Columns
    from rich.text import Text

    lines = [
        "  [bold red]What it does[/bold red]",
        "  Simulates public reaction to any scenario using AI agent swarms.",
        "  Builds a knowledge graph · generates personas · runs social media sim.",
        "  Results open in your browser at [red]localhost:3000[/red]",
        "",
        "  [bold red]Commands[/bold red]",
        "  [red]megafish[/red]                run a simulation",
        "  [red]megafish update[/red]         update to the latest version",
        "  [red]megafish uninstall[/red]      uninstall MegaFish",
        "  [red]megafish status[/red]         show status of all services",
        "  [red]megafish stop[/red]           stop all running services",
        "  [red]megafish help[/red]           show this info",
    ]
    content = "\n".join(lines)
    console.print(Panel(content, border_style="red", padding=(0, 1)))
    console.print()


def prompt_box() -> str:
    console.print(Panel(
        "[red]Enter a scenario to simulate:[/red]\n"
        "[dim]e.g. 'Apple announces $500 iPhone'  ·  'NATO expands to include Ukraine'[/dim]\n\n"
        "[dim]Press Ctrl+C to exit[/dim]",
        border_style="bold red",
        title="[bold red]  Scenario  [/bold red]",
        padding=(1, 2),
    ))
    value = Prompt.ask("[bold red]  >[/bold red]")
    console.print()
    return value


def ask_file() -> str | None:
    answer = Prompt.ask("[red]Attach a file? (path or Enter to skip)[/red]", default="")
    return answer.strip() or None


def status(msg: str):
    console.print(f"[red]●[/red] {msg}")


def success(msg: str):
    console.print(f"[bold red]✓[/bold red] {msg}")


def error(msg: str):
    err_console.print(f"[bold red]✗[/bold red] {msg}")


def progress(msg: str):
    from rich.progress import Progress, SpinnerColumn, TextColumn
    return Progress(
        SpinnerColumn(style="red"),
        TextColumn(f"[red]{msg}[/red]"),
        console=console,
    )
