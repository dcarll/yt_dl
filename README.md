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

Para o funcionamento correto do download de vídeos em alta resolução e conversão para MP3, é necessário ter o **FFmpeg** instalado no sistema ou o executável `ffmpeg.exe` na pasta raiz do projeto.

---

## 🚀 Como configurar o ambiente

Siga os passos abaixo para preparar o ambiente e rodar o projeto localmente.

### 1. Clonar o repositório
```bash
git clone https://github.com/dcarll/yt_dl.git
cd yt_dl
```

### 2. Criar um Ambiente Virtual (Venv)
O uso de um ambiente virtual é recomendado para manter as dependências do projeto isoladas.

**No Windows:**
```bash
python -m venv .venv
```

**No Linux/macOS:**
```bash
python3 -m venv .venv
```

### 3. Ativar o Ambiente Virtual

**No Windows:**
```bash
.venv\Scripts\activate
```

**No Linux/macOS:**
```bash
source .venv/bin/activate
```

### 4. Instalar Dependências
Com o ambiente virtual ativo, instale os pacotes necessários:
```bash
pip install -r requirements.txt
```

---

## 💻 Como usar

Após configurar o ambiente, basta executar o arquivo principal:

```bash
python main.py
```

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
