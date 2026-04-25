@echo off
setlocal enabledelayedexpansion

:: Define o título da janela
title Iniciar Aplicativo

:: Muda para o diretório onde o .bat está localizado para garantir caminhos relativos
cd /d "%~dp0"

echo ========================================================
echo Verificando requisitos do sistema...
echo ========================================================

:: 1. Verifica se o Python está instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] O Python nao foi encontrado ou nao esta nas variaveis de ambiente ^(PATH^).
    echo Por favor, instale o Python marcando a opcao "Add Python to PATH" durante a instalacao.
    pause
    exit /b
)
echo [OK] Python esta instalado.

:: Ativa o ambiente virtual (.venv) se existir
if exist ".venv\Scripts\activate.bat" (
    echo [INFO] Ambiente virtual encontrado. Ativando...
    call .venv\Scripts\activate.bat
)

:: 2. Instala/verifica bibliotecas requeridas
if exist "requirements.txt" (
    echo [INFO] Verificando e instalando bibliotecas necessarias...
    pip install -r requirements.txt >nul 2>&1
    if %errorlevel% neq 0 (
         echo [AVISO] Pode ter ocorrido um erro ao instalar dependencias. Exibindo log completo:
         pip install -r requirements.txt
    ) else (
         echo [OK] Bibliotecas atualizadas.
    )
)

:: 3. Verifica o ffmpeg.exe na raiz
if not exist "ffmpeg.exe" (
    echo [INFO] ffmpeg.exe nao encontrado. Preparando para baixar...
    
    set "FFMPEG_URL=https://www.gyan.dev/ffmpeg/builds/packages/ffmpeg-2026-04-22-git-162ad61486-essentials_build.7z"
    set "ARQUIVO_7Z=ffmpeg_temp.7z"
    
    echo [INFO] Baixando FFmpeg ^(!FFMPEG_URL!^)...
    :: Baixa o arquivo .7z usando PowerShell
    powershell -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '!FFMPEG_URL!' -OutFile '!ARQUIVO_7Z!'"
    
    if exist "!ARQUIVO_7Z!" (
        echo [INFO] Arquivo baixado. Extraindo o ffmpeg.exe...
        
        :: Cria diretorio temporario para extracao
        mkdir ffmpeg_temp_dir 2>nul
        
        :: Usa tar nativo para tentar extrair
        tar -xf "!ARQUIVO_7Z!" -C ffmpeg_temp_dir
        
        :: Se falhar, tentamos usar a biblioteca py7zr com python
        if %errorlevel% neq 0 (
             echo [AVISO] Falha na extracao com tar. Tentando via py7zr instalando temporariamente...
             pip install py7zr >nul 2>&1
             python -c "import py7zr; archive=py7zr.SevenZipFile('!ARQUIVO_7Z!', mode='r'); archive.extractall('ffmpeg_temp_dir'); archive.close();"
        )

        :: Localiza o ffmpeg.exe dentro da pasta bin extraída e move para a raiz, conforme pedido
        for /d %%d in (ffmpeg_temp_dir\*) do (
            if exist "%%d\bin\ffmpeg.exe" (
                move /Y "%%d\bin\ffmpeg.exe" .\ >nul
            )
        )
        :: Se o loop acima falhar, fazemos um fallback global pesquisando o arquivo .exe
        if not exist "ffmpeg.exe" (
            for /r "ffmpeg_temp_dir" %%i in (ffmpeg.exe) do (
                if exist "%%i" (
                    move /Y "%%i" .\ >nul
                )
            )
        )
        
        :: 4. Limpeza
        echo [INFO] Apagando arquivos baixados desnecessarios...
        if exist "ffmpeg_temp_dir" rmdir /S /Q ffmpeg_temp_dir
        if exist "!ARQUIVO_7Z!" del /Q "!ARQUIVO_7Z!"
        
        if exist "ffmpeg.exe" (
            echo [OK] ffmpeg.exe instalado com sucesso na pasta raiz.
        ) else (
            echo [ERRO] Ocorreu um problema e o ffmpeg.exe nao foi encontrado apos a tentativa de extracao.
            pause
            exit /b
        )
    ) else (
        echo [ERRO] Nao foi possivel baixar o ffmpeg da URL fornecida. O link pode estar invalido.
        pause
        exit /b
    )
) else (
    echo [OK] ffmpeg.exe ja esta presente na raiz do projeto.
)

echo ========================================================
echo Iniciando o programa...
echo ========================================================

:: 5. Iniciar o programa principal
if exist "main.py" (
    python main.py
) else (
    echo [ERRO] arquivo main.py nao encontrado na pasta atual! Nao e possivel iniciar.
    pause
)
