import requests
import io
import os
import zipfile
from pathlib import Path
from rich.console import Console
from rich.progress import (
    Progress,
    DownloadColumn,
    TransferSpeedColumn,
    TextColumn,
    TimeRemainingColumn,
    BarColumn,
)

console = Console()

progress_layout = Progress(
    TextColumn("[bold blue]{task.fields[filename]}", justify="right"),
    BarColumn(bar_width=None),
    "[progress.percentage]{task.percentage:>3.1f}%",
    "•",
    DownloadColumn(),
    "•",
    TransferSpeedColumn(),
    "•",
    TimeRemainingColumn(),
    console=console,
    transient=True,
)


def server_download(server_type, test=False):
    """Gerencia o download e setup inicial do servidor.

    Nota: faz import local de funções de UI quando necessário para evitar
    importação circular ao reorganizar os pacotes.
    """

    # Importações locais para não criar ciclo na carga de módulos
    from easymcserver.ui.menus import (
        select_dir,
        get_bedrock_download_link,
        get_java_download_link,
    )

    # Define o diretório de saída com base no tipo de servidor
    if test:
        test_dir = Path(r"Z:\test")
        if test_dir.exists():
            # usar o diretório de testes já existente
            if input(
                "Já há um teste com esse nome, deseja usá-lo? (S/n)"
            ).strip().upper() in ["S", ""]:
                return test_dir

            else:
                i = 1
                while True:
                    test_dir_new = Path(f"{test_dir}{str(i)}")
                    if test_dir_new.exists():
                        i += 1
                    else:
                        output_dir = test_dir_new
                        break
        else:
            output_dir = test_dir

    else:
        output_dir = select_dir(server_type)

    # --- Lógica Bedrock ---
    if server_type == "Bedrock":
        link = get_bedrock_download_link()
        filename = "bedrock_server.zip"

        zip_content = download_file_with_progress(link, filename, output_dir)

        if zip_content:
            console.print("[cyan]Extraindo arquivos Bedrock...[/cyan]")
            try:
                # O BytesIO é usado pois o arquivo foi baixado para a memória
                with zipfile.ZipFile(zip_content, "r") as zip_ref:
                    zip_ref.extractall(output_dir)
                console.print(
                    "[bold green][OK][/bold green] Arquivos Bedrock extraídos."
                )
                return output_dir
            except zipfile.BadZipFile:
                console.print(
                    "[bold red][ERRO][/bold red] O arquivo baixado não é um ZIP válido. Verifique o link."
                )
            except Exception as e:
                console.print(f"[bold red]ERRO na extração:[/bold red] {e}")
            return False  # Falha na extração
        return False  # Falha no download

    # --- Lógica Java ---
    elif server_type in [
        "Vanilla",
        "Paper (Otimizado)",
        "NeoForge (Mods)",
        "Fabric (Mods)",
    ]:

        if server_type == "Vanilla":
            if test:
                download_url = "https://piston-data.mojang.com/v1/objects/64bb6d763bed0a9f1d632ec347938594144943ed/server.jar"

            else:
                download_url = get_java_download_link()

            filename = "server.jar"

        else:
            return False  # Tipo não suportado

        # --- Download ---

        if download_file_with_progress(download_url, filename, output_dir):
            # Criar EULA
            eula_path = os.path.join(output_dir, "eula.txt")
            with open(eula_path, "w") as f:
                f.write("eula=true\n")
            console.print("[bold green][OK][/bold green] EULA aceito automaticamente.")
            return output_dir
        return False  # Falha no download

    else:
        console.print(
            f"[bold red]AVISO:[/bold red] Tipo de servidor '{server_type}' não suportado ainda."
        )
        return False


def download_file_with_progress(url: str, filename: str, output_dir: str):
    """
    Baixa um arquivo de uma URL e exibe o progresso usando Rich.
    Retorna True/False para sucesso ou o objeto BytesIO para ZIPs.
    """
    full_path = os.path.join(output_dir, filename)
    os.makedirs(output_dir, exist_ok=True)

    console.print(f"[yellow]Baixando: {filename} em '{output_dir}'...[/yellow]")
    console.print(f"[cyan]URL: {url}[/cyan]")

    try:
        with progress_layout as progress:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            response = requests.get(url, stream=True, headers=headers, timeout=30)
            console.print(f"[cyan]Status code: {response.status_code}[/cyan]")
            if "content-length" in response.headers:
                console.print(
                    f"[cyan]Content-Length: {response.headers['content-length']}[/cyan]"
                )
            else:
                console.print("[yellow]No Content-Length header[/yellow]")
            response.raise_for_status()

            total_size = int(response.headers.get("content-length", 0))
            if total_size == 0:
                console.print(
                    "[yellow]AVISO:[/yellow] Não foi possível determinar o tamanho do arquivo."
                )
                total_size = 1024 * 1024 * 100

            download_task = progress.add_task(
                "Baixando", total=total_size, filename=filename
            )

            if filename.endswith(".zip"):
                content = io.BytesIO()
                f = None
            else:
                content = None
                f = open(full_path, "wb")

            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    if filename.endswith(".zip"):
                        content.write(chunk)
                    else:
                        f.write(chunk)
                    progress.update(download_task, advance=len(chunk))

            if f:
                f.close()

            progress.update(download_task, completed=total_size)
            console.print(f"[bold green][OK][/bold green] '{filename}' baixado.")

            return content if filename.endswith(".zip") else True

    except requests.exceptions.RequestException as e:
        console.print(
            f"[bold red]ERRO de Download:[/bold red] Não foi possível baixar '{filename}'. Detalhes: {e}"
        )
        return False
    except Exception as e:
        console.print(f"[bold red]ERRO:[/bold red] Ocorreu um erro inesperado: {e}")
        return False
