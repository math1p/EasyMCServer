import os
from psutil import virtual_memory
from rich.panel import Panel
from rich.console import Console
from importlib.metadata import version
version_str = version("easyminecraftserver")

console = Console()

def display_header():
    """Exibe o cabeçalho formatado do script."""
    console.print(
        Panel(f"[bold cyan]>>> EasyMinecraftServer {version_str} | math1p <<<[/bold cyan]", 
              border_style="green"), 
        justify="center"
    )
    console.print()

def clear():
    if os.name == 'nt':
        os.system('cls')
    elif os.name == 'linux':
        os.system('clear')
        
    display_header()
    
def get_sys_memory():
    """Obtém informações de memória do sistema."""
    mem_info = virtual_memory()
    total_ram_gb = round(mem_info.total / (1024**3), 2)
    available_ram_gb = round(mem_info.available / (1024**3), 2)
    used_ram_gb = round(mem_info.used / (1024**3), 2)
    return total_ram_gb, available_ram_gb, used_ram_gb
