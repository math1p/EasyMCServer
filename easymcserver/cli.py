import time
import os
import zipfile
import subprocess  # Para rodar o JAR ou o instalador
from jproperties import Properties
from InquirerPy import prompt
from rich.console import Console
from pathlib import Path
from easymcserver.download import download_file_with_progress
from easymcserver.utils import clear, get_sys_memory

console = Console()

BEDROCK_SERVER_URL = "https://www.minecraft.net/pt-br/download/server/bedrock"
JAVA_SERVER_URL = "https://www.minecraft.net/pt-br/download/server"

# --- --- ---


def check_java_installed():
    """Verifica se o Java está instalado e retorna a versão."""
    try:
        result = subprocess.run(
            ["java", "-version"], capture_output=True, text=True, check=True
        )
        # A saída de java -version vai para stderr
        version_line = result.stderr.split("\n")[0]
        console.print(f"[green]Java detectado: {version_line}[/green]")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        console.print(
            "[bold red][ERRO][/bold red] Java não está instalado ou não está no PATH."
        )
        console.print(
            "[yellow]Instale o Java (JDK 17 ou superior) de https://adoptium.net/ e tente novamente.[/yellow]"
        )
        return False


def get_java_server_type():
    """Menu para escolher o tipo de servidor Java."""
    questions = [
        {
            "type": "list",
            "name": "java_type",
            "message": "Escolha o tipo de servidor Java:",
            "choices": ["Vanilla"],
            #'choices': ['Vanilla', 'Paper (Otimizado)', 'NeoForge (Mods)', 'Fabric (Mods)'],
        }
    ]
    return prompt(questions)["java_type"]


def get_memory_config_input_xmx():
    """Pergunta a alocação máxima de memória (Xmx) - Personalizado."""
    questions = [
        {
            "type": "input",
            "name": "memory",
            "message": "RAM Máxima (Xmx):",
            "default": "4G",
        }
    ]
    return prompt(questions)["memory"]


def get_memory_config_input_xms():
    """Pergunta a alocação mínima de memória (Xms) - Personalizado."""
    questions = [
        {
            "type": "input",
            "name": "memory_xms",
            "message": "RAM Mínima (Xms):",
            "default": "512M",
        }
    ]
    return prompt(questions)["memory_xms"]


def get_memory_config_xmx():
    """Pergunta a alocação máxima de memória (Xmx) - Seleção."""
    questions = [
        {
            "type": "list",
            "name": "memory_xmx",
            "message": "Quantidade máxima de memória (Xmx):",
            "choices": ["2G", "4G", "8G", "16G"],
        }
    ]
    return prompt(questions)["memory_xmx"]


def get_memory_config_xms():
    """Pergunta a alocação mínima de memória (Xms) - Seleção."""
    questions = [
        {
            "type": "list",
            "name": "memory_xms",
            "message": "Quantidade mínima de memória (Xms):",
            "choices": ["512M", "1G", "2G", "4G"],
        }
    ]
    return prompt(questions)["memory_xms"]


def get_memory_menu(total_ram_gb):
    """Gerencia o menu de configuração de RAM com validação."""
    while True:
        try:
            questions = [
                {
                    "type": "list",
                    "name": "mode",
                    "message": f"Total de RAM do Sistema: {total_ram_gb} GB. Configure a memória disponível para a JVM:",
                    "choices": ["Predefinido", "Personalizado"],
                }
            ]

            result = prompt(questions)
            choice = result["mode"]

            if choice == "Predefinido":
                memory_xmx = get_memory_config_xmx()
                memory_xms = get_memory_config_xms()

            elif choice == "Personalizado":

                # --- Configuração Xmx (Máxima) ---
                while True:
                    try:
                        memory_xmx = get_memory_config_input_xmx()
                        value_gb_xmx = (
                            float(memory_xmx.replace("G", ""))
                            if "G" in memory_xmx.upper()
                            else float(memory_xmx.replace("M", "")) / 1024
                        )

                        if (
                            "G" not in memory_xmx.upper()
                            and "M" not in memory_xmx.upper()
                        ):
                            raise ValueError
                        if value_gb_xmx > total_ram_gb:
                            raise MemoryError
                        break
                    except ValueError:
                        console.print(
                            "[bold red][ERRO][/bold red] Digite valores inteiros com M ou G (Ex.: 512M ou 4G)"
                        )
                    except MemoryError:
                        console.print(
                            "[bold red][ERRO][/bold red] RAM Máxima excede a disponível no sistema."
                        )

                # --- Configuração Xms (Mínima) ---
                while True:
                    try:
                        memory_xms = get_memory_config_input_xms()
                        value_gb_xms = (
                            float(memory_xms.replace("G", ""))
                            if "G" in memory_xms.upper()
                            else float(memory_xms.replace("M", "")) / 1024
                        )

                        if (
                            "G" not in memory_xms.upper()
                            and "M" not in memory_xms.upper()
                        ):
                            raise ValueError
                        # Simplificação: Apenas verificar se o Xms não excede o total disponível
                        if value_gb_xms > total_ram_gb:
                            raise MemoryError

                        if value_gb_xms > value_gb_xmx:
                            raise MemoryError

                        break
                    except ValueError:
                        console.print(
                            "[bold red][ERRO][/bold red] Digite valores inteiros com M ou G (Ex.: 512M ou 4G)"
                        )
                    except MemoryError:
                        console.print(
                            "[bold red][ERRO][/bold red] RAM Mínima excede a disponível no sistema ou Xms é igual a Xmx, o que não pode acontecer."
                        )

            return memory_xmx, memory_xms

        except KeyboardInterrupt:
            raise
        except Exception as e:
            # Mantido para segurança.
            console.print(
                f"[bold red]ERRO Desconhecido no Menu de Memória: {e}[/bold red]"
            )
            time.sleep(1)
            continue


# --- --- ---


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
                    f"[yellow]AVISO:[/yellow] O diretório '{full_path}' já existe."
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


def server_download(server_type):
    """Gerencia o download e setup inicial do servidor."""

    # Define o diretório de saída com base no tipo de servidor
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
            download_url = get_java_download_link()
            filename = "server.jar"

        #        elif server_type == 'Paper (Otimizado)':
        #            download_url = None
        #            filename = "server.jar"

        #        elif server_type in ['NeoForge (Mods)', 'Fabric (Mods)']:
        #            # Lógica para baixar o instalador e executar via subprocess
        #            console.print("[yellow]AVISO:[/yellow] A lógica de instalação de Mods (NeoForge/Fabric) não está implementada.")
        #            return False

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


# --- Menu ---


def main_menu():
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
                total_ram_gb, available_ram_gb, used_ram_gb = get_sys_memory()

                result = prompt(questions)
                choice = result["edition"]
                version = choice

                if choice == "Sair":
                    console.print("\n[bold red]Instalação cancelada![/bold red]")
                    break

                elif choice == "Java":
                    if not check_java_installed():
                        input('Pressione "Enter" para continuar... ')
                        clear()
                        continue
                    server_type = get_java_server_type()

                    output_dir = server_download(server_type)
                    if not output_dir:
                        input('Pressione "Enter" para continuar... ')
                        clear()
                        continue  # Volta ao menu se o download/setup falhar

                    memory_xmx, memory_xms = get_memory_menu(total_ram_gb)

                    # Criação do Script de Inicialização Java
                    create_start_script("Java", output_dir, memory_xmx, memory_xms)

                    console.print(
                        f"\n[cyan]Instalação Java concluída:[/cyan] Tipo: {server_type}, RAM: Xms {memory_xms}, Xmx {memory_xmx}.\n"
                    )

                elif choice == "Bedrock":
                    console.print(
                        "\n[cyan]Configuração escolhida:[/cyan] Bedrock Dedicated Server. (Não requer configuração de RAM)"
                    )

                    output_dir = server_download("Bedrock")
                    if not output_dir:
                        input('Pressione "Enter" para continuar... ')
                        clear()
                        continue  # Volta ao menu se o download/setup falhar

                    # Criação do Script de Inicialização Bedrock
                    create_start_script("Bedrock", output_dir)

                    console.print("\n[cyan]Instalação Bedrock concluída!\n[/cyan]")

                questions = [
                    {
                        "type": "list",
                        "name": "edit_quit",
                        "message": "Selecione uma opção:",
                        "choices": ["Editar o server.properties", "Sair"],
                    }
                ]
                result = prompt(questions)
                choice = result["edit_quit"]
                if choice == "Sair":
                    quit()
                else:
                    if version == "Java":
                        console.print(
                            "[red]Atenção![/red] O serivdor precisa ser iniciado ao menos uma vez para gerar o arquivo server.properties."
                        )
                        questions = [
                            {
                                "type": "confirm",
                                "name": "start_server",
                                "message": "O servidor será iniciado, deseja continuar?",
                                "default": False,
                            }
                        ]
                        if not prompt(questions)["start_server"]:
                            quit()
                        else:
                            auto_start_stop_java(output_dir)
                            server_properties(output_dir, "Java")
                    else:
                        server_properties(output_dir, "Bedrock")

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
                    console.print(
                        f"[green]Diretório existente selecionado: {path}[/green]"
                    )
                    directory = str(path)

                    server_properties(directory)

                else:
                    console.print(
                        f"[red][ERRO][/red] O caminho '{path}' não existe ou não é um diretório."
                    )

                break

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


# --- Configurar (server.properties) ---


def server_properties(directory, version=None):
    """Função para ler e editar o arquivo server.properties"""

    caminho_arquivo = os.path.join(directory, "server.properties")

    if not os.path.exists(caminho_arquivo):
        console.print(f"[red][ERRO][/red] Arquivo não encontrado em {caminho_arquivo}")
        return
    else:
        console.print(
            f"[bold green][OK][/bold green] o arquivo [blue]{caminho_arquivo}[/blue] foi aberto para edição"
        )
    if version == None:
        questions = [
            {
                "type": "list",
                "name": "version_properties",
                "message": "Selecione a versão do servidor que terá o server.properties modificado:",
                "choices": ["Java", "Bedrock"],
            }
        ]
        result = prompt(questions)
        choice = result["version_properties"]

        version = choice

    # 1. Carregar as propriedades atuais
    configs = Properties()
    with open(caminho_arquivo, "rb") as f:
        configs.load(f)

    # 2. Definir quais chaves você quer oferecer para edição
    if version == "Java":
        chaves_para_editar = [
            "level-name",
            "difficulty",
            "gamemode",
            "max-players",
            "online-mode",
            "generate-structures",
            "spawn-protection",
            "view-distance",
            "simulation-distance",
            "server-port",
            "motd",
        ]

    elif version == "Bedrock":
        chaves_para_editar = [
            "level-name",
            "difficulty",
            "gamemode",
            "max-players",
            "online-mode",
            "allow-cheats",
            "max-threads",
            "view-distance",
            "simulation-distance",
            "server-port",
            "server-name",
        ]

    # 3. Gerar a lista de perguntas dinamicamente com base nas chaves pré-selecionadas
    questions = []
    for chave in chaves_para_editar:
        # Pega o valor atual ou string vazia se não existir
        valor_atual = configs.get(chave).data if configs.get(chave) else ""

        questions.append(
            {
                "type": "input",
                "name": chave,
                "message": f"Configurar {chave}:",
                "default": str(valor_atual),  # Aqui está o pulo do gato
            }
        )

    # 4. Mostrar os prompts ao usuário
    respostas = prompt(questions)

    # Se o usuário cancelar ou o dicionário vier vazio, interrompe
    if not respostas:
        return

    # 5. Aplicar as respostas de volta ao objeto configs
    for chave, novo_valor in respostas.items():
        configs[chave] = str(novo_valor)

    # 6. Salvar o arquivo preservando comentários e estrutura
    with open(caminho_arquivo, "wb") as f:
        configs.store(f, encoding="utf-8")

    console.print("\n[bold green][OK][/bold green] server.properties atualizado!")
    quit()


def auto_start_stop_java(directory):

    command = "start.bat" if os.name == "nt" else "./start.sh"

    # Iniciamos o processo com pipes para entrada e saída
    process = subprocess.Popen(
        command,
        cwd=directory,
        shell=True,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,  # Redireciona erros para a saída comum
        text=True,  # Garante que lidamos com strings, não bytes
        bufsize=1,  # Buffer de linha para leitura em tempo real
    )

    console.print(
        "[bold green][OK][/bold green] Iniciando o servidor para gerar arquivos. Isso pode demorar um pouco..."
    )

    # Loop para monitorar a saída do terminal em tempo real
    while True:
        linha = process.stdout.readline()
        if not linha:
            break

        # Mostra a linha no seu terminal (opcional)
        # print(linha.strip())

        # O Minecraft avisa que terminou com a mensagem "Done"
        if "Done" in linha:
            console.print(
                "[bold green][OK][/bold green] Servidor foi carregado e os arquivos foram gerados. Enviando comando 'stop'...\n"
            )

            # Envia o comando 'stop' seguido de uma quebra de linha
            process.stdin.write("stop\n")
            process.stdin.flush()  # Garante que o comando saia do Python e chegue no Java
            break

    # Aguarda o processo encerrar completamente
    # process.wait()
    # print("Servidor encerrado e arquivos gerados com sucesso.")


def main():
    main_menu()
