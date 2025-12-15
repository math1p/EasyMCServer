import requests
import io
import os
from rich.console import Console
from rich.progress import (
    Progress, 
    DownloadColumn, 
    TransferSpeedColumn, 
    TextColumn, 
    TimeRemainingColumn, 
    BarColumn
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
    transient=True
)

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
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            response = requests.get(url, stream=True, headers=headers, timeout=30)
            console.print(f"[cyan]Status code: {response.status_code}[/cyan]")
            if 'content-length' in response.headers:
                console.print(f"[cyan]Content-Length: {response.headers['content-length']}[/cyan]")
            else:
                console.print("[yellow]No Content-Length header[/yellow]")
            response.raise_for_status() 

            total_size = int(response.headers.get("content-length", 0))
            if total_size == 0:
                console.print("[yellow]AVISO:[/yellow] Não foi possível determinar o tamanho do arquivo.")
                total_size = 1024 * 1024 * 100
            
            download_task = progress.add_task(
                "Baixando", 
                total=total_size, 
                filename=filename
            )

            if filename.endswith('.zip'):
                content = io.BytesIO()
                f = None
            else:
                content = None
                f = open(full_path, "wb")

            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    if filename.endswith('.zip'):
                        content.write(chunk)
                    else:
                        f.write(chunk)
                    progress.update(download_task, advance=len(chunk))
            
            if f:
                f.close()
                
            progress.update(download_task, completed=total_size) 
            console.print(f"[bold green]SUCESSO:[/bold green] '{filename}' baixado.")
            
            return content if filename.endswith('.zip') else True

    except requests.exceptions.RequestException as e:
        console.print(f"[bold red]ERRO de Download:[/bold red] Não foi possível baixar '{filename}'. Detalhes: {e}")
        return False
    except Exception as e:
        console.print(f"[bold red]ERRO:[/bold red] Ocorreu um erro inesperado: {e}")
        return False
