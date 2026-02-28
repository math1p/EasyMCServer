from rich.console import Console
from importlib.metadata import version
import subprocess
import platform
import os

console = Console()


def check_java_installed(return_version_only=False):
    """Verifica se o Java está instalado e retorna a versão."""
    try:
        result = subprocess.run(
            ["java", "-version"], capture_output=True, text=True, check=True
        )
        # A saída de java -version vai para stderr
        version_line = result.stderr.split("\n")[0]
        if return_version_only is True:
            return version_line
        else:
            console.print(
                f"[bold green][OK][/bold green] Java detectado: {version_line}"
            )
            return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        console.print(
            "[bold red][ERRO][/bold red] O Java não está instalado ou não está no PATH. Instale-o e tente novamente."
        )
        return False


def check_box64_installed():
    try:
        result = subprocess.run(["box64", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            return True, result.stdout.splitlines()[0]
    except FileNotFoundError:
        return False, None


def check_sys_arch():
    return platform.machine()


if __name__ == "__main__":
    check_sys_arch()
