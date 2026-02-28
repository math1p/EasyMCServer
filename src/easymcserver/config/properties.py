import os
import subprocess
from InquirerPy import prompt
from rich.console import Console

console = Console()


def server_properties(directory, version=None):
    """Função para ler e editar o arquivo server.properties"""

    server_properties_path = os.path.join(directory, "server.properties")

    if not os.path.exists(server_properties_path):
        console.print(
            "[bold yellow][Atenção][/bold yellow] O serivdor precisa ser iniciado ao menos uma vez para gerar o arquivo server.properties."
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
            return
        else:
            auto_start_stop_java(directory)

    if not os.path.exists(server_properties_path):
        console.print(
            f"[red][ERRO][/red] Arquivo não encontrado em {server_properties_path}"
        )
        return
    else:
        console.print(
            f"[bold green][OK][/bold green] o arquivo [blue]{server_properties_path}[/blue] foi aberto para edição"
        )
    if version is None:
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

        # não pode ser choice = result...?

    # 1. Carregar as propriedades atuais (import local para evitar erro se a
    # dependência não estiver instalada no ambiente de checagem)
    try:
        from jproperties import Properties
    except Exception as e:
        console.print(
            f"[bold red][ERRO][/bold red] Biblioteca 'jproperties' não está disponível: {e}"
        )
        return

    configs = Properties()
    with open(server_properties_path, "rb") as f:
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
                "default": str(valor_atual),
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
    with open(server_properties_path, "wb") as f:
        configs.store(f, encoding="utf-8")

    console.print(
        "[bold green][OK][/bold green] O arquivo server.properties atualizado!\n"
    )
    return


def auto_start_stop_java(directory):

    command = "start.bat" if os.name == "nt" else "./start.sh"

    # Iniciamos o processo com pipes para entrada e saída
    process = subprocess.Popen(
        command,
        cwd=directory,
        shell=True,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    console.print(
        "[bold green][OK][/bold green] Iniciando o servidor para gerar arquivos. Isso pode demorar um pouco..."
    )

    # Loop para monitorar a saída do terminal em tempo real
    while True:
        linha = process.stdout.readline()
        if not linha:
            break

        # O Minecraft avisa que terminou com a mensagem "Done"
        if "Done" in linha:
            console.print(
                "[bold green][OK][/bold green] Servidor foi carregado e os arquivos foram gerados. Enviando comando 'stop'...\n"
            )

            # Envia o comando 'stop' seguido de uma quebra de linha
            process.stdin.write("stop\n")
            process.stdin.flush()
            break


if __name__ == "__main__":
    auto_start_stop_java("")
