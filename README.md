# 🎬 YT Downloader Pro

Uma ferramenta poderosa e elegante para baixar vídeos e áudios do YouTube, construída com **Python**, **Flet** e **yt-dlp**.

![Versão](https://img.shields.io/badge/vers%C3%A3o-1.0.0-red)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![Flet](https://img.shields.io/badge/UI-Flet-orange)

## ✨ Funcionalidades

- 📥 **Vídeo Único:** Baixe vídeos em diversas qualidades (dependendo da disponibilidade no YouTube).
- 📋 **Playlists:** Baixe playlists inteiras de uma só vez.
- 🎵 **Áudio MP3:** Converta e baixe apenas o áudio em alta qualidade.
- 📊 **Progresso em Tempo Real:** Barra de progresso visual e estimativa de tempo (ETA).
- 📂 **Seleção de Pasta:** Escolha facilmente onde quer salvar seus arquivos.
- 🌓 **Interface Moderna:** Design limpo e intuitivo.

## 🛠️ Pré-requisitos

Para o funcionamento correto de download de vídeos em alta resolução e conversão para MP3, é necessário o **Python** e o executável **FFmpeg**.

- **Python**: Instale a versão mais recente e **certifique-se de marcar a opção "Add Python to PATH"** durante a instalação.
- **FFmpeg**: O nosso inicializador automático (`iniciar.bat`) fará o download e configurará o FFmpeg sozinho. Se você quiser fazer tudo manualmente, ele também pode ser baixado e colado na pasta raiz.

---

## 🚀 Como Executar

Escolha uma das maneiras de execução abaixo de acordo com sua experiência!

### 🌟 O Jeito Fácil (Apenas um clique / Recomendado)

Na pasta do projeto, dê um duplo clique no arquivo **`iniciar.bat`**. 
Ele é automatizado para fazer tudo por você:
- Verifica a instalação do Python.
- Configura e injeta as dependências/bibliotecas automaticamente através do arquivo de requisitos.
- Procura o executável do **FFmpeg**. Se não achar, não se preocupe: fará o download e extração tudo em segundo plano!
- Abre a aplicação na sua tela.

### 🛠️ O Jeito Manual (Via Terminal / Venv)

Caso você tenha conhecimentos técnicos e deseje usar pela linha de comando:

#### 1. Clonar o Repositório
```bash
git clone https://github.com/dcarll/yt_dl.git
cd yt_dl
```

#### 2. Criar e Ativar Ambiente Virtual
Criar um ambiente isola as dependências desse projeto do resto do seu computador.
**No Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```
**No Linux/macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

#### 3. Instalar Dependências Necessárias
```bash
pip install -r requirements.txt
```

#### 4. Configurar FFmpeg Manualmente
- Baixe o pacote oficial [através deste link](https://www.gyan.dev/ffmpeg/builds/packages/ffmpeg-2026-04-22-git-162ad61486-essentials_build.7z).
- Extraia os arquivos do `.7z`, abra a pasta extraída, entre em `bin` e pegue o arquivo **`ffmpeg.exe`**.
- Copie e cole na mesma pasta de onde o `main.py` repousa.

#### 5. Inicialização
```bash
python main.py
```

---

## 💻 Como usar

1. **🎬 VÍDEOS:** Cole o link, clique em **Buscar** para ver as qualidades, selecione uma e clique em **Baixar**.
2. **🎵 ÁUDIOS:** Mude para a aba de Áudio, cole o link e clique em **Baixar MP3**.
3. **📂 ABRIR PASTA:** Use o botão de pasta para acessar rapidamente seus downloads.

---

## 📦 Gerar Executável (.exe)

O projeto já inclui um arquivo `.spec` para o PyInstaller. Para gerar o executável:

```bash
pip install pyinstaller
flet pack main.py --name "YTDownloaderPro"
```

---

## 📄 Licença

Este projeto está sob a licença [MIT](LICENSE).

---
Desenvolvido por [dcarll](https://github.com/dcarll)
