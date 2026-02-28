import os
from rich.panel import Panel
from rich.console import Console


version_str = "0.2.0"

console = Console()


def display_header():
    """Exibe o cabeçalho formatado do script."""
    console.print(
        Panel(
            f"[bold cyan]>>> EasyMCServer v{version_str} | math1p <<<[/bold cyan]",
            border_style="green",
        ),
        justify="center",
    )
    console.print()


def clear():
    if os.name == "nt":
        os.system("cls")
    elif os.name == "linux":
        os.system("clear")

    display_header()


def create_start_script(server_type, output_dir, xmx=None, xms=None):
    """Cria o script de inicialização (start.sh ou start.bat)."""

    if os.name == "nt":  # Windows
        script_name = "start.bat"
        # O Bedrock usa o .exe
        if server_type == "Bedrock":
            script_content = "bedrock_server.exe"
        # O Java usa o java.exe
        else:
            script_content = f"java -Xmx{xmx} -Xms{xms} -jar server.jar nogui\npause"

    else:  # Linux/macOS
        script_name = "start.sh"
        if server_type == "Bedrock":
            script_content = "./bedrock_server"
        else:
            script_content = (
                f"#!/bin/bash\njava -Xmx{xmx} -Xms{xms} -jar server.jar nogui"
            )

    script_path = os.path.join(output_dir, script_name)

    with open(script_path, "w") as f:
        f.write(script_content)

    if os.name != "nt":
        os.chmod(script_path, 0o755)  # Permissão de execução no Linux/macOS

    console.print(
        f"[bold green][OK][/bold green] Script de inicialização '{script_name}' criado em {output_dir}."
    )
