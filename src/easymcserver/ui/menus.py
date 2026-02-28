import time
import os
from InquirerPy import prompt
from rich.console import Console
from pathlib import Path
from easymcserver.downloader.download import server_download
from easymcserver.utils import clear, create_start_script
from easymcserver.config.properties import server_properties
from easymcserver.config.jvm_args import edit_jvm_args_file
from easymcserver.system.sys_info import (
    check_java_installed,
    check_sys_arch,
    check_box64_installed,
)
from easymcserver.system.memory import (
    get_sys_memory,
    get_memory_config_xmx,
    get_memory_config_xms,
)

console = Console()

BEDROCK_SERVER_URL = "https://www.minecraft.net/pt-br/download/server/bedrock"
JAVA_SERVER_URL = "https://www.minecraft.net/pt-br/download/server"


def main_menu(test=False):
    """Menu principal do instalador."""
    clear()

    questions = [
        {
            "type": "list",
            "name": "mode",
            "message": "O que deseja fazer?",
            "choices": ["Instalar", "Configurar", "Sair"],
        }
    ]

    result = prompt(questions)
    choice = result["mode"]

    if choice == "Instalar":

        questions = [
            {
                "type": "list",
                "name": "edition",
                "message": "Qual edição do Minecraft deseja instalar?",
                "choices": ["Java", "Bedrock", "Sair"],
            }
        ]

        while True:
            try:
                total_ram_gb, avaliable_ram_gb, used_ram_gb = get_sys_memory()

                result = prompt(questions)
                choice = result["edition"]

                if choice == "Sair":
                    console.print("\n[bold red]Instalação cancelada![/bold red]")
                    break

                elif choice == "Java":
                    if not java_selected(total_ram_gb, avaliable_ram_gb, test):
                        continue  # Volta ao menu se o download/setup falhar
                    else:
                        java_selected()

                elif choice == "Bedrock":
                    if not bedrock_selected():
                        continue  # Volta ao menu se o download/setup falhar
                    else:
                        bedrock_selected()

            except KeyboardInterrupt:
                console.print(
                    "\n[bold red]Operação interrompida pelo usuário (Ctrl+C).[/bold red]"
                )
                break
            except Exception as e:
                console.print(f"\n[bold red]Ocorreu um erro inesperado: {e}[/bold red]")
                break

    elif choice == "Configurar":
        while True:
            try:
                if test:
                    questions = [
                        {
                            "type": "input",
                            "name": "path",
                            "message": "Caminho do diretório raíz do servidor:",
                            "default": str(Path("Z:\\test")),
                        }
                    ]
                else:
                    questions = [
                        {
                            "type": "input",
                            "name": "path",
                            "message": "Caminho do diretório raíz do servidor:",
                            "default": str(Path.cwd())
                            + ("\\" if os.name == "nt" else "/")
                            + "MinecraftServer",
                        }
                    ]

                path_str = prompt(questions)["path"]
                path = Path(path_str.strip('"'))

                if path.exists() and path.is_dir():
                    while True:
                        console.print(
                            f"[green]Diretório existente selecionado: {path}[/green]"
                        )
                        directory = str(path)

                        questions = [
                            {
                                "type": "list",
                                "name": "edit_quit",
                                "message": "Selecione uma opção:",
                                "choices": [
                                    "Editar o server.properties",
                                    "Editar as flags da JVM (apenas Java)",
                                    "Sair",
                                ],
                            }
                        ]
                        result = prompt(questions)
                        choice = result["edit_quit"]
                        if choice == "Sair":
                            quit()
                        elif choice == "Editar o server.properties":
                            server_properties(directory)
                        else:
                            edit_jvm_args_file(directory, "w")

                else:
                    console.print(
                        f"[red][ERRO][/red] O caminho '{path}' não existe ou não é um diretório."
                    )
                    input('Pressione "Enter" para continuar... ')

            except KeyboardInterrupt:
                console.print(
                    "\n[bold red]Operação interrompida pelo usuário (Ctrl+C).[/bold red]"
                )
                break
            except Exception as e:
                console.print(f"\n[bold red]Ocorreu um erro inesperado: {e}[/bold red]")
                break

    else:
        console.print("\n[bold red]Saindo...[/bold red]")


def get_bedrock_download_link():
    """Pergunta o link do Bedrock."""
    console.print(f"[bold green]Acesse: {BEDROCK_SERVER_URL}[bold green]")
    questions = [
        {
            "type": "input",
            "name": "link",
            "message": "Cole o link de download (URL) do Bedrock Server disponível no link acima ou escolha outra versão de sua preferência:",
            "default": "",
        }
    ]
    return prompt(questions)["link"]


def get_java_download_link():
    """Pergunta o link do Java"""
    console.print(f"[bold green]Acesse: {JAVA_SERVER_URL}[bold green]")
    questions = [
        {
            "type": "input",
            "name": "link",
            "message": "Cole o link de download (URL) do Java Server disponível no link acima ou escolha outra versão de sua preferência em https://mcversions.net/:",
            "default": "",
        }
    ]
    return prompt(questions)["link"]


def select_dir(server_type):
    """Permite ao usuário escolher onde instalar o servidor."""
    questions = [
        {
            "type": "list",
            "name": "choice",
            "message": "Onde deseja instalar o servidor?",
            "choices": ["Diretório padrão", "Novo diretório", "Diretório existente"],
        }
    ]
    choice = prompt(questions)["choice"]

    if choice == "Diretório padrão":
        output_dir = f"./{server_type.lower().replace(' (mods)', '').replace(' (otimizado)', '').replace(' ', '_')}_server"
        console.print(f"[cyan]Diretório padrão selecionado: {output_dir}[/cyan]")
        return output_dir

    elif choice == "Novo diretório":
        while True:
            questions = [
                {
                    "type": "input",
                    "name": "path",
                    "message": "Caminho base para o novo diretório:",
                    "default": str(Path.cwd()),
                },
                {
                    "type": "input",
                    "name": "name",
                    "message": "Nome do novo diretório:",
                    "default": f"Minecraft-{server_type}",
                },
            ]
            answers = prompt(questions)
            base_path = Path(answers["path"])
            dir_name = answers["name"]
            full_path = base_path / dir_name
            if full_path.exists():
                console.print(
                    f"[yellow][AVISO][/yellow] O diretório '{full_path}' já existe."
                )
                questions = [
                    {
                        "type": "confirm",
                        "name": "overwrite",
                        "message": "Deseja usar o diretório existente?",
                        "default": False,
                    }
                ]
                if prompt(questions)["overwrite"]:
                    console.print(
                        f"[green]Usando diretório existente: {full_path}[/green]"
                    )
                    return str(full_path)
                else:
                    continue
            else:
                console.print(f"[green]Novo diretório será criado: {full_path}[/green]")
                return str(full_path)

    elif choice == "Diretório existente":
        while True:
            questions = [
                {
                    "type": "input",
                    "name": "path",
                    "message": "Caminho do diretório existente:",
                    "default": str(Path.cwd()),
                }
            ]
            path_str = prompt(questions)["path"]
            path = Path(path_str)
            if path.exists() and path.is_dir():
                console.print(f"[green]Diretório existente selecionado: {path}[/green]")
                return str(path)
            else:
                console.print(
                    f"[red][ERRO][/red] O caminho '{path}' não existe ou não é um diretório."
                )
                continue


def bedrock_selected():
    arch = check_sys_arch()
    if "arm" in arch.lower() or "aarch64" in arch.lower():
        console.print(
            f"[bold yellow][AVISO][/bold yellow] Arquitetura do processador: {arch}"
        )
        if check_box64_installed()[0]:
            console.print(
                f"[bold green][OK][/bold green] O Box64 está instalado! O Servidor Bedrock funcionará perfeitamente.\nBox64: {check_box64_installed[1]}"
            )
        else:
            console.print(
                "[bold red][ERRO][/bold red] O Servidor Bedrock não suporta processadores ARM, o Box64 deve ser instalado para prosseguir."
            )
            input('Pressione "Enter" para continuar... ')
            clear()
            return False
    else:
        console.print(
            f"[bold green][OK][/bold green] Arquitetura do processador: {arch}"
        )

    console.print(
        "\n[cyan]Configuração escolhida:[/cyan] Bedrock Dedicated Server (Não requer configuração de RAM)"
    )

    output_dir = server_download("Bedrock")
    if not output_dir:
        input('Pressione "Enter" para continuar... ')
        clear()
        return

    # Criação do Script de Inicialização Bedrock
    create_start_script("Bedrock", output_dir)

    console.print("\n[cyan]Instalação Bedrock concluída!\n[/cyan]")
    while True:
        questions = [
            {
                "type": "list",
                "name": "edit_quit",
                "message": "Selecione uma opção:",
                "choices": [
                    "Editar o server.properties",
                    "Sair",
                ],
            }
        ]
        result = prompt(questions)
        choice = result["edit_quit"]
        if choice == "Sair":
            quit()
        else:
            server_properties(output_dir, "Bedrock")


def java_selected(total_ram_gb, avaliable_ram_gb, test):
    if not check_java_installed():
        input('Pressione "Enter" para continuar... ')
        clear()
        return

    server_type = get_java_server_type(test)

    output_dir = server_download(server_type, test)

    if not output_dir:
        input('Pressione "Enter" para continuar... ')
        clear()
        return

    memory_xmx, memory_xms = get_memory_menu(total_ram_gb, avaliable_ram_gb)

    # Criação do Script de Inicialização Java
    create_start_script("Java", output_dir, memory_xmx, memory_xms)

    console.print(
        f"\n[cyan]Instalação Java concluída:[/cyan] Tipo: {server_type}, RAM: Xms {memory_xms}, Xmx {memory_xmx}.\n"
    )
    while True:

        questions = [
            {
                "type": "list",
                "name": "edit_quit",
                "message": "Selecione uma opção:",
                "choices": [
                    "Editar o server.properties",
                    "Editar as flags da JVM",
                    "Sair",
                ],
            }
        ]
        result = prompt(questions)
        choice = result["edit_quit"]
        if choice == "Sair":
            quit()
        elif choice == "Editar o server.properties":
            server_properties(output_dir, "Java")
        else:
            edit_jvm_args_file(output_dir, "w")


def get_java_server_type(test=False):
    """Menu para escolher o tipo de servidor Java."""

    if test:
        return "Vanilla"

    else:
        questions = [
            {
                "type": "list",
                "name": "java_type",
                "message": "Escolha o tipo de servidor Java:",
                "choices": ["Vanilla"],
            }
        ]
        return prompt(questions)["java_type"]


def get_memory_menu(total_ram_gb, avaliable_ram_gb):
    """Gerencia o menu de configuração de RAM com validação."""
    while True:
        try:
            console.print(
                f"Total de RAM do Sistema: [cyan]{total_ram_gb} GB[/cyan], RAM disponível para uso: [cyan]{avaliable_ram_gb} GB[/cyan]. Configure a memória disponível para a JVM:"
            )
            questions = [
                {
                    "type": "list",
                    "name": "mode",
                    "message": "Selecione o modo de alocação de memória da JVM:",
                    "choices": ["Predefinido", "Customizado"],
                }
            ]

            result = prompt(questions)
            choice = result["mode"]

            while True:

                if choice == "Predefinido":
                    memory_xmx, test_xmx = get_memory_config_xmx()
                    if memory_xmx is False:
                        # Reinicia o loop
                        break
                    memory_xms, test_xms = get_memory_config_xms()
                    if memory_xms is False:
                        break

                elif choice == "Customizado":
                    # --- Configuração Xmx (Máxima) ---
                    memory_xmx, test_xmx = get_memory_config_xmx(custom=True)
                    if memory_xmx is False:
                        break

                    # --- Configuração Xms (Mínima) ---
                    memory_xms, test_xms = get_memory_config_xms(custom=True)

                if memory_xms is False:
                    break

                else:
                    if test_xms > test_xmx:
                        xms_fmt = f"{memory_xms[:-1]} {memory_xms[-1:]}"
                        xmx_fmt = f"{memory_xmx[:-1]} {memory_xmx[-1:]}"

                        console.print(
                            f"[bold yellow][AVISO][/bold yellow] O parâmetro Xms ([cyan]{xms_fmt}B[/cyan]) "
                            f"é maior que o Xmx ([cyan]{xmx_fmt}B[/cyan])! "
                            f"O valor de Xmx será ajustado para [green]{xms_fmt}B[/green]."
                        )
                        memory_xmx = memory_xms
                    if test_xms > avaliable_ram_gb:
                        console.print(
                            f"[bold yellow][AVISO][/bold yellow] A quantidade de memória alocada para a JVM é maior do que a disponível para uso no sistema ([cyan]{avaliable_ram_gb} GB[/cyan]). Se o swap (ou pagefile.sys) for utilizado, a performance do servidor será severamente prejudicada."
                        )
                    return memory_xmx, memory_xms

        except KeyboardInterrupt:
            raise
        except Exception as e:
            # Mantido para segurança.
            console.print(
                f"[bold red][ERRO][/bold red] Ocorreu um erro desconhecido no Menu de Memória: {e}"
            )
            time.sleep(1)
            continue
