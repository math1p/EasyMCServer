from easymcserver.cli import main
from rich.console import Console

console = Console()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        console.print(f"Erro fatal: {e}")
        input("Pressione Enter para sair...")
