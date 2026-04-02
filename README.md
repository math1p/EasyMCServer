# EasyMCServer

O EasyMCServer é uma ferramente CLI feita em Python para facilitar a instalação/configuração rápida de servidores de Minecraft (Java e Bedrock) em qualquer dispositivo.

## Para que?

Testar as configurações ideais para um servidor pode ser uma tarefa trabalhosa mesmo para aqueles que já possuem alguma experiência na área, mas pode ser ainda mais desafiadora para quem não está familiarizado com redes e sistemas operacionais. Por isso, essa ferramenta foca principalmente em simplificar e agilizar tanto a instalação e a configuração de servidores de Minecraft para que qualquer um possa ter o seu próprio servidor. Além disso, o programa é capaz alertar sobre possíveis problemas que podem surgir no caminho, como: alocação excessiva de RAM para a JVM, Java não instalado/encontrado e arquitetura incompatível (Bedrock não suporta ARM nativamente).

## Como usar?

 Instale o programa com `pip install easymcserver` (é necessário ter o Python 3 instalado caso esteja no Windows) ou baixe o executável `.exe` (somente Windows) disponível em "Releases".

> [!TIP]
No Linux, instalar pacotes junto ao sistema pode não ser uma boa ideia, prefira instlalar o programa em um ambiente virtual com:
`python3 -m venv venv` e `source venv/bin/activate`
No entanto, existe uma método mais moderno para instalar um programa com pip tanto no Linux quanto no Windows, ele (o pipx) cuida do ambiente virtual sozinho e facilita o processo. Experimente com: `pipx install easymcserver`. No Ubuntu será necessário usar os comandos: `sudo apt update` e `sudo apt install pipx`, além de `pipx ensurepath`. No Windows basta usar `pip install pipx` (com o Python já instalado). Em outras distros Linux basta adaptar o comando para usar o gerenciador de pacotes da distribuição utilizada, ex.: `sudo dnf install pipx`, para o Fedora.

Excute o programa com `easymc` no terminal ou execute o .exe (somente Windows) e verá uma tela parecida com essa: 

> ![alt text](image-1.png)

Aqui é possível ver que há duas opções: "Instalar" e "Configurar"

 - Instalar: Selecione o tipo de servidor que deseja instalar (Java ou Bedrock)

 - Configurar: Selecione o diretório (a pasta) raíz do servidor. Ex.: Se o arquivo .jar/.exe está em `"C:\\Users\\mathe\\Minecraft-Server\\\\EXECUTÁVEL\_DO\_SERVIDOR"` 

### Avisos e Erros

### Avisos:

### Erros:

- Java não instalado/detectado: O java não foi encontrado pois provavelmente não está instalado ou não está no PATH.

- Memória excedida: A quantidade de memória alocada para a JVM não pode ser superior a quantidade de RAM disponível no sistema.
