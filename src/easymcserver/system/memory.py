from psutil import virtual_memory
from InquirerPy import prompt
from rich.console import Console

console = Console()


def get_sys_memory():
    """Obtém informações de memória do sistema."""
    mem_info = virtual_memory()
    total_ram_gb = round(mem_info.total / (1024**3), 2)
    available_ram_gb = round(mem_info.available / (1024**3), 2)
    used_ram_gb = round(mem_info.used / (1024**3), 2)
    return total_ram_gb, available_ram_gb, used_ram_gb


def get_memory_config_xmx(custom: bool = False):
    if custom:
        """Pergunta a alocação máxima de memória (Xmx) - Customizado."""
        questions = [
            {
                "type": "input",
                "name": "memory_xmx",
                "message": "RAM Máxima (Xmx):",
                "default": "4G",
            }
        ]
        return validate_mem_config(prompt(questions)["memory_xmx"])

    else:
        """Pergunta a alocação máxima de memória (Xmx) - Seleção."""
        questions = [
            {
                "type": "list",
                "name": "memory_xmx",
                "message": "Quantidade máxima de memória (Xmx):",
                "choices": ["2G", "4G", "8G", "16G"],
            }
        ]
        return validate_mem_config(prompt(questions)["memory_xmx"])


def get_memory_config_xms(custom: bool = False):
    if custom:
        """Pergunta a alocação mínima de memória (Xms) - Customizado."""
        questions = [
            {
                "type": "input",
                "name": "memory_xms",
                "message": "RAM Mínima (Xms):",
                "default": "512M",
            }
        ]
        return validate_mem_config(prompt(questions)["memory_xms"])

    else:
        """Pergunta a alocação mínima de memória (Xms) - Seleção."""
        questions = [
            {
                "type": "list",
                "name": "memory_xms",
                "message": "Quantidade mínima de memória (Xms):",
                "choices": ["512M", "1G", "2G", "4G"],
            }
        ]
        return validate_mem_config(prompt(questions)["memory_xms"])


def validate_mem_config(value: str):
    try:
        if not value:
            return False

        total_ram_gb, _, _ = get_sys_memory()

        value = value.upper().strip()

        if "G" in value:
            # manter em GB
            value = float(value.replace("G", ""))
            unit = "G"
        elif "M" in value:
            # converter MB para GB
            value = float(value.replace("M", "")) / 1024
            unit = "M"
        else:
            raise ValueError

        if value > total_ram_gb:
            raise MemoryError

    except ValueError:
        console.print(
            '[bold red][ERRO][/bold red] Digite valores inteiros com "M" para Megabyte ou "G" para Gigabyte (Ex.: 512M ou 4G)'
        )
        return False, None
    except MemoryError:
        console.print(
            f"[bold red][ERRO][/bold red] A quantidade de memória alocada para a JVM excede o total disponível no sistema ([cyan]{total_ram_gb} GB[/cyan])."
        )
        return False, None

    if unit == "G":
        if value == int(value):
            return str(int(value)) + "G", int(value)
        else:
            # transfomar em MB se o valor em GB for quebrado
            value = value * 1024
            return str(int(value)) + "M", int(value)

    elif unit == "M":
        # transformar os GB em MB de volta e retornar também uma segunda variável em GB
        return str(int(value * 1024)) + "M", int(value)
    else:
        return False
