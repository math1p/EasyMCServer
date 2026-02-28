# Argumentos da JMV

import os
from InquirerPy import prompt, inquirer
from rich.console import Console
from easymcserver.system.sys_info import check_java_installed

console = Console()


def edit_jvm_args_file(directory, mode="r"):
    # Versão, PATH e lista de argumentos
    java_version_raw = check_java_installed(True)
    if not java_version_raw:
        return
    console.print(f"[bold green][OK][/bold green] Java detectado: {java_version_raw}")
    java_version = format_java_version_string(java_version_raw)
    # Se a versão detectada não for uma das pré-definidas, pergunte ao usuário se ele deseja escolher uma versão para gerar o arquivo.
    if not java_version:
        console.print(
            f"[bold red][ERRO][/bold red] A edição de flags da JVM não suporta essa versão do Java: {check_java_installed(True)}"
        )

        manual_selected_java_version = inquirer.select(
            message="Deseja gerar um arquivo com base em alguma dessas versões?",
            choices=["1.8", "17", "21", "25", "Sair"],
            default="Sair",
        ).execute()

        if manual_selected_java_version == "Sair":
            return
        else:
            java_version = manual_selected_java_version
            console.print(
                "[bold yellow][AVISO][/bold yellow] Não há garantia de que as flags funcionarão nessa versão!"
            )
    jvm_args_path = os.path.join(directory, "jvm_args.txt")
    jvm_args_list = determine_jvm_args_list(java_version)
    if not jvm_args_list:
        console.print(
            "[bold red][ERRO][/bold red] Ocorreu um erro ao determinar as flags da JVM!"
        )
        input('Pressione "Enter" para continuar... ')
        return

    # Verificar se o arquivo existe
    if not os.path.exists(jvm_args_path) or os.path.getsize(jvm_args_path) == 0:
        # Caso não exista ou esteja em branco:
        restore_jvm_args_file(jvm_args_path, jvm_args_list, java_version)

    # Se o arquivo existir, verifica se ele foi criado para a versão do java atual
    if os.path.exists(jvm_args_path):
        java_version_in_file = None
        with open(jvm_args_path, "r", encoding="utf-8") as f:
            for line in f:
                # Verifica se a linha contém a info do Java
                if "java version:" in line.lower():
                    # Pega apenas o número da versão
                    parts = line.split(":")
                    if len(parts) > 1:
                        java_version_in_file = parts[1].strip()
                    break

            if java_version_in_file and float(java_version_in_file) != float(
                java_version
            ):
                console.print(
                    f"[bold yellow][AVISO][/bold yellow] O arquivo jvm_args.txt foi criado para o Java [cyan]{java_version_in_file}[/cyan], "
                    f"mas você está usando o Java [cyan]{java_version}[/cyan]."
                )
                questions = [
                    {
                        "type": "confirm",
                        "name": "overwrite",
                        "message": "Deseja atualizar as sugestões de flags para a versão atual?",
                        "default": True,
                    }
                ]
                if prompt(questions)["overwrite"]:
                    restore_jvm_args_file(jvm_args_path, jvm_args_list, java_version)

            elif float(java_version_in_file) == float(java_version):
                console.print(
                    "[bold green][OK][/bold green] As sugestões de flags são compatíveis com essa versão do Java."
                )

    if mode == "r":
        with open(jvm_args_path, "r", encoding="utf-8") as file:
            return file.read()

    elif mode == "w":
        try:
            with open(jvm_args_path, "r", encoding="utf-8") as file:
                lines = file.readlines()
        except FileNotFoundError:
            lines = []  # Caso o arquivo seja deletado na edição

        garbage_collector_options = []
        memory_config_options = []
        perf_flags_options = []
        others_options = []
        active_flags = []
        section = "others"

        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue

            # Busca por seção
            lower_line = stripped.lower()
            if "garbage collector" in lower_line:
                section = "gb_collector"
                continue
            elif "memory config" in lower_line:
                section = "mem_config"
                continue
            elif "performance flags" in lower_line:
                section = "perf_flags"
                continue
            elif "others" in lower_line:
                section = "others"
                continue

            # Captura as flags ativas e inativas
            if stripped.startswith("#-") or stripped.startswith("-"):
                # Remove # e espaços extras para garantir comparação limpa
                clean_flag = normalize(stripped.lstrip("#"))

                # Linhas ativas
                if stripped.startswith("-"):
                    active_flags.append(normalize(clean_flag))

                if section == "gb_collector":
                    garbage_collector_options.append(clean_flag)
                elif section == "mem_config":
                    memory_config_options.append(clean_flag)
                elif section == "perf_flags":
                    perf_flags_options.append(clean_flag)
                elif section == "others":
                    others_options.append(clean_flag)

        try:
            # 1. Seleção Única (GC)
            if garbage_collector_options:
                current_gc = next(
                    (
                        f
                        for f in garbage_collector_options
                        if normalize(f) in active_flags
                    ),
                    garbage_collector_options[0],
                )

                garbage_collector_flags = inquirer.select(
                    message="Selecione o Garbage Collector:",
                    choices=garbage_collector_options,
                    default=current_gc,
                ).execute()
            else:
                garbage_collector_flags = []

            # 2, 3, 4. Seleções Múltiplas
            if memory_config_options:
                current_mem = [
                    f for f in memory_config_options if normalize(f) in active_flags
                ]
                memory_choices = [
                    {"name": flag, "value": flag, "enabled": flag in active_flags}
                    for flag in memory_config_options
                ]

                memory_config_flags = inquirer.checkbox(
                    message="Selecione as flags de Memória:",
                    choices=memory_choices,
                    cycle=True,
                    transformer=lambda result: f"{len(result)} flags selecionadas",
                ).execute()
            else:
                memory_config_flags = []

            if perf_flags_options:
                current_perf = [
                    f for f in perf_flags_options if normalize(f) in active_flags
                ]
                perf_choices = [
                    {"name": flag, "value": flag, "enabled": flag in active_flags}
                    for flag in perf_flags_options
                ]

                perf_flags = inquirer.checkbox(
                    message="Selecione as flags de Performance:",
                    choices=perf_choices,
                    default=current_perf,
                    cycle=True,
                    transformer=lambda result: f"{len(result)} flags selecionadas",
                ).execute()
            else:
                perf_flags = []

            if others_options:
                current_others = [
                    f for f in others_options if normalize(f) in active_flags
                ]
                others_choices = [
                    {"name": flag, "value": flag, "enabled": flag in active_flags}
                    for flag in others_options
                ]

                others_flags = inquirer.checkbox(
                    message="Selecione outras flags:",
                    choices=others_options,
                    default=current_others,
                    cycle=True,
                    transformer=lambda result: f"{len(result)} flags selecionadas",
                ).execute()
            else:
                others_flags = []

            # O check 'if garbage_collector_flags' evita erros de concatenação
            all_selected_flags = set(
                ([garbage_collector_flags] if garbage_collector_flags else [])
                + (memory_config_flags or [])
                + (perf_flags or [])
                + (others_flags or [])
            )

            # Gravação do arquivo
            with open(jvm_args_path, "w", encoding="utf-8") as file:
                for line in lines:
                    stripped = line.strip()

                    if stripped.startswith("-") or stripped.startswith("#-"):
                        raw_flag = normalize(stripped.lstrip("#"))

                        if raw_flag in all_selected_flags:
                            file.write(f"{raw_flag}\n")  # Ativa no arquivo
                        else:
                            file.write(f"#{raw_flag}\n")  # Comenta no arquivo
                    else:
                        file.write(line if line.endswith("\n") else line + "\n")

            console.print(
                "[bold green][OK][/bold green] Configurações salvas com sucesso!\n"
            )

        except KeyboardInterrupt:
            console.print(
                "\n[bold yellow][AVISO][/bold yellow] Edição cancelada. Nenhuma alteração foi salva."
            )
            return  # Sai da função sem abrir o arquivo para escrita


def normalize(flag: str) -> str:
    return flag.strip().replace("\r", "")


def view_jvm_args(directory):
    jvm_args = edit_jvm_args_file(directory, "r")
    list_of_args = ""
    for line in jvm_args:
        if line.strip() and not line.startswith("#"):
            # console.print(f"[bold blue]{line}[/bold blue]")
            list_of_args += f"{line.strip()}\n"
    return list_of_args


def format_java_version_string(java_version_raw):
    # Encontra a versão através dos números após 'java version' em java version "25.0.2" 2026-01-20 LTS
    only_number = java_version_raw[14:]
    if only_number.strip().startswith("1.8"):
        return "1.8"
    elif only_number.strip().startswith("17"):
        return "17"
    elif only_number.strip().startswith("21"):
        return "21"
    elif only_number.strip().startswith("25"):
        return "25"
    else:
        return False

    # Removido pois não era capaz de identificar o Java 8 (1.8) e outras versões com nomenclatura 1.x
    """
    # Encontra a versão atráves das aspas e dos pontos em java version "25.0.2" 2026-01-20 LTS
    java_version_formated = ""
    version_is_here = False
    for i in java_version_raw:
        if version_is_here:
            if i == '"' or i == "'":
                break
            java_version_formated += i
        if i == '"' or i == "'":
            version_is_here = True
    java_version = ""
    for i in java_version_formated:
        if i == ".":
            break
        java_version += i
    return java_version
    """


def restore_jvm_args_file(jvm_args_path, jvm_args_list, java_version):
    with open(jvm_args_path, "w", encoding="utf-8") as file:
        file.write(
            f'# Não apague a linha "java version"! \n'
            f"#java version: {java_version}\n\n"
            f"# --- Garbage Collector ---\n"
            f"#{'\n#'.join(jvm_args_list[0])}\n\n"
            f"# --- Memory Config ---\n"
            f"#{'\n#'.join(jvm_args_list[1])}\n\n"
            f"# --- Performance Flags ---\n"
            f"#{'\n#'.join(jvm_args_list[2])}"
            f"\n\n# --- Others ---\n"
        )


def determine_jvm_args_list(java_version):

    garbage_collector = [
        "-XX:+UseG1GC",  # Equilibrado (Padrão para Java 17, 21, 25)
        "-XX:+UseZGC",  # Baixa latência (Java 17+)
        "-XX:+ZGenerational",  # Ultra-fluidez (Habilitado no Java 25, experimental no 21)
        "-XX:+UseShenandoahGC",  # Baixa latência alternativo (Java 17+)
        "-XX:+UseConcMarkSweepGC",  # Legado (Apenas Java 8)
    ]

    mem_manager = [
        "-XX:+AlwaysPreTouch",  # Aloca toda a RAM ao iniciar (Evita engasgos durante o jogo)
        "-XX:+UseCompactObjectHeaders",  # NOVO: Java 25 (Reduz uso de RAM em ~20%)
        "-XX:G1HeapRegionSize=32M",  # Otimiza carregamento de chunks grandes
    ]

    optimizing_perf = [
        "-XX:+ParallelRefProcEnabled",  # Acelera limpeza de objetos
        "-XX:+DisableExplicitGC",  # Impede que mods forcem limpezas lentas (System.gc)
        "-XX:MaxGCPauseMillis=50",  # Meta de latência: 50ms para manter 20 TPS
        "-XX:+PerfDisableSharedMem",  # Reduz IO desnecessário no disco/SSD
        "-XX:G1NewSizePercent=30",  # Garante espaço para entidades e partículas novas
        "-XX:-DontCompileHugeMethods",  # Permite compilação de métodos gigantes comuns em mods
    ]

    match float(java_version):
        case 1.8:
            jvm_args_list = (
                [garbage_collector[0], garbage_collector[4]],
                [mem_manager[0], mem_manager[2]],
                optimizing_perf,
            )
        case 17:
            jvm_args_list = (
                [garbage_collector[0], garbage_collector[1], garbage_collector[3]],
                [mem_manager[0], mem_manager[2]],
                optimizing_perf,
            )
        case 21:
            jvm_args_list = (
                garbage_collector[:4],
                [mem_manager[0], mem_manager[2]],
                optimizing_perf,
            )
        case 25:
            jvm_args_list = (
                garbage_collector[:4],
                mem_manager,
                optimizing_perf,
            )
        case _:
            console.print(
                "[bold red][ERRO][/bold red] Ocorreu um erro ao identificar a versão do java instalada."
            )
            print(java_version)

    return jvm_args_list


if __name__ == "__main__":
    format_java_version_string(check_java_installed(True))
    determine_jvm_args_list(None)
