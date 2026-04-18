"""
main.py — YouTube Downloader App
Built with Flet (Flutter for Python) + yt-dlp
Highly compatible with Flet 0.82+ / 1.0
"""
import threading
import subprocess
import os
import sys
import webbrowser
import flet as ft
import downloader
import tkinter as tk
from tkinter import filedialog


# ─────────────────────────────────────────────
#  Path Helpers for EXE
# ─────────────────────────────────────────────
def get_resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# ─────────────────────────────────────────────
#  Colour constants
# ─────────────────────────────────────────────
BG_COLOR       = "#f5f6f7"
SURFACE        = "#ffffff"
SURFACE2       = "#f0f2f5" 
ACCENT         = "#e00000"
ACCENT2        = "#ff3333"
TEXT_PRIMARY   = "#1c1e21"
TEXT_SECONDARY = "#606770"
BORDER         = "#dadde1"
SUCCESS        = "#28a745"
ERROR_COLOR    = "#dc3545"


def _btn_style(primary: bool) -> ft.ButtonStyle:
    if primary:
        return ft.ButtonStyle(
            bgcolor={"": ACCENT, ft.ControlState.HOVERED: ACCENT2, ft.ControlState.DISABLED: "#cccccc"},
            color={"": "#ffffff"},
            shape=ft.RoundedRectangleBorder(radius=10),
            padding=ft.Padding.symmetric(horizontal=24, vertical=12),
        )
    return ft.ButtonStyle(
        bgcolor={"": SURFACE2, ft.ControlState.HOVERED: "#e4e6eb"},
        color={"": TEXT_PRIMARY},
        shape=ft.RoundedRectangleBorder(radius=10),
        side=ft.BorderSide(1, BORDER),
        padding=ft.Padding.symmetric(horizontal=16, vertical=10),
    )


def gap(h: int) -> ft.Container:
    return ft.Container(height=h)


class LabelButton:
    def __init__(self, label_text: str, primary: bool = True, disabled: bool = False, icon=None):
        self._text_obj = ft.Text(label_text)
        # Using ft.FilledButton (Flet 0.82+ way)
        self.ctrl = ft.FilledButton(
            content=self._text_obj,
            icon=icon,
            style=_btn_style(primary),
            disabled=disabled,
        )

    @property
    def text(self): return self._text_obj.value
    @text.setter
    def text(self, value): 
        self._text_obj.value = value
    @property
    def disabled(self): return self.ctrl.disabled
    @disabled.setter
    def disabled(self, value): self.ctrl.disabled = value
    @property
    def on_click(self): return self.ctrl.on_click
    @on_click.setter
    def on_click(self, fn): self.ctrl.on_click = fn


async def main(page: ft.Page):
    page.title = "YT Downloader Pro"
    page.bgcolor = BG_COLOR
    page.window.width = 850
    page.window.height = 850
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0

    # ── FFmpeg Discovery ─────────────────────────
    ffmpeg_path = [None] 

    def check_ffmpeg():
        local_exe = "ffmpeg.exe" if os.name == "nt" else "ffmpeg"
        paths_to_check = [get_resource_path(local_exe), os.path.abspath(local_exe)]
        for p in paths_to_check:
            if os.path.exists(p):
                ffmpeg_path[0] = str(p)
                return True
        try:
            subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
            ffmpeg_path[0] = "ffmpeg"
            return True
        except:
            pass
        return False

    has_ffmpeg = check_ffmpeg()

    # ── UI Elements ──────────────────────────────
    snack_bar = ft.SnackBar(ft.Text(""), bgcolor=SUCCESS)
    page.overlay.append(snack_bar)

    async def snack(msg: str, color=SUCCESS):
        snack_bar.content.value = msg
        snack_bar.bgcolor = color
        snack_bar.open = True
        page.update()

    def open_folder(path):
        if os.name == "nt":
            if os.path.exists(path):
                os.startfile(path)
            else:
                page.run_task(snack, "Pasta não encontrada!", ERROR_COLOR)
        else:
            page.run_task(snack, "Funcionalidade de abrir pasta disponível apenas no Windows.", TEXT_SECONDARY)

    # ── Helpers ──────────────────────────────────
    def make_url_field(hint: str) -> ft.TextField:
        return ft.TextField(
            hint_text=hint, bgcolor=SURFACE, color=TEXT_PRIMARY,
            border_color=BORDER, focused_border_color=ACCENT,
            border_radius=10, text_size=14, expand=True,
        )

    def make_path_field(label: str) -> ft.TextField:
        default_p = os.path.join(os.path.expanduser("~"), "Downloads")
        return ft.TextField(
            label=label, value=default_p, bgcolor=SURFACE, color=TEXT_PRIMARY,
            border_color=BORDER, focused_border_color=ACCENT,
            border_radius=10, text_size=12,
        )

    def make_dropdown(label: str) -> ft.Dropdown:
        return ft.Dropdown(
            label=label, bgcolor=SURFACE, color=TEXT_PRIMARY,
            border_color=BORDER, focused_border_color=ACCENT,
            border_radius=10, visible=False,
        )

    # ── File Picker (Native Fallback) ────────────
    def open_picker_sync(target_field):
        # Create a hidden root for tkinter
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)  # Make it appear on top
        path = filedialog.askdirectory(title="Selecione a pasta de download")
        root.destroy()
        if path:
            target_field.value = path
            target_field.update()
            page.update()

    def open_picker(target_field):
        # Run in thread to not block Flet's event loop
        page.run_thread(open_picker_sync, target_field)

    # ══════════════════════════════════════════════
    #  TAB VIDEOS
    # ══════════════════════════════════════════════
    vid_url  = make_url_field("Cole o link do vídeo aqui...")
    vid_drop = make_dropdown("Qualidade disponível")
    vid_path = make_path_field("Salvar em")
    pick_v_btn = ft.IconButton(ft.Icons.FOLDER_OPEN, on_click=lambda _: open_picker(vid_path), tooltip="Alterar pasta")
    
    vid_prog = ft.ProgressBar(value=0, color=ACCENT, bgcolor="#eeeeee", height=8, border_radius=4)
    vid_stat = ft.Text("Pronto para buscar", color=TEXT_SECONDARY, size=12)
    
    fetch_btn = LabelButton("🔍 Buscar", primary=False)
    dl_btn    = LabelButton("🚀 Baixar Vídeo", primary=True, disabled=True)
    open_btn  = LabelButton("📂 Abrir Pasta", primary=False, icon=ft.Icons.FOLDER_OPEN)

    async def on_fetch(e):
        url = vid_url.value.strip()
        if not url: await snack("Insira um link!", ERROR_COLOR); return
        fetch_btn.disabled = True
        fetch_btn.text = "Buscando..."
        vid_drop.visible = False
        vid_stat.value = "Consultando YouTube..."
        page.update()
        
        def do_fetch():
            try:
                fmts = downloader.fetch_formats(url)
                if fmts:
                    vid_drop.options = [ft.dropdown.Option(f["format_id"], f["label"]) for f in fmts]
                    vid_drop.value = fmts[0]["format_id"]
                    vid_drop.visible = True
                    dl_btn.disabled = False
                    vid_stat.value = "Selecione a qualidade e baixe."
                else: 
                    vid_stat.value = "Nenhuma qualidade encontrada."
                    vid_drop.visible = False
            except Exception as ex: 
                vid_stat.value = f"Erro ao buscar: {ex}"
                vid_drop.visible = False
            finally: 
                fetch_btn.disabled = False
                fetch_btn.text = "🔍 Buscar"
                page.run_thread(page.update)
        
        threading.Thread(target=do_fetch, daemon=True).start()
    
    fetch_btn.on_click = on_fetch

    async def on_dl(e):
        url, fmt, folder = vid_url.value.strip(), vid_drop.value, vid_path.value.strip()
        if not os.path.exists(folder): os.makedirs(folder, exist_ok=True)
        dl_btn.disabled = True
        vid_prog.value = 0
        vid_stat.value = "Iniciando..."
        page.update()
        
        def progress(p, s, eta):
            vid_prog.value = p/100
            vid_stat.value = f"Baixando: {p:.1f}% | {s} | ETA: {eta}"
            page.run_thread(page.update)

        def done(m):
            vid_prog.value = 1
            vid_stat.value = f"✅ {m}"
            dl_btn.disabled = False
            page.run_task(snack, m)
            page.run_thread(page.update)

        def error(m):
            vid_stat.value = f"❌ Erro: {m}"
            dl_btn.disabled = False
            page.run_task(snack, m, ERROR_COLOR)
            page.run_thread(page.update)

        downloader.download_video(url, fmt, folder, progress, done, error, ffmpeg_path[0])
    
    dl_btn.on_click = on_dl
    open_btn.on_click = lambda e: open_folder(vid_path.value.strip())

    # Playlist Video
    pv_url   = make_url_field("Link da playlist de vídeos...")
    pv_path  = make_path_field("Salvar playlist em")
    pick_pv  = ft.IconButton(ft.Icons.FOLDER_OPEN, on_click=lambda _: open_picker(pv_path), tooltip="Alterar pasta")
    
    pv_prog  = ft.ProgressBar(value=0, color=ACCENT, bgcolor="#eeeeee", height=8)
    pv_stat  = ft.Text("", color=TEXT_SECONDARY, size=12)
    pv_dl    = LabelButton("📋 Baixar Playlist")
    pv_open  = LabelButton("📂 Abrir Pasta", primary=False, icon=ft.Icons.FOLDER_OPEN)

    async def on_pv_dl(e):
        url, folder = pv_url.value.strip(), pv_path.value.strip()
        if not url: await snack("Link vazio!", ERROR_COLOR); return
        if not os.path.exists(folder): os.makedirs(folder, exist_ok=True)
        pv_dl.disabled = True
        pv_prog.value = 0
        page.update()
        
        downloader.download_playlist_video(url, "bestvideo[height<=1080]+bestaudio/best", folder, 
            lambda p,s,eta: (setattr(pv_prog, "value", p/100), setattr(pv_stat, "value", f"{p:.1f}% | {s}"), page.run_thread(page.update)),
            lambda m: (page.run_task(snack, m), setattr(pv_dl, "disabled", False), page.run_thread(page.update)),
            lambda m: (page.run_task(snack, m, ERROR_COLOR), setattr(pv_dl, "disabled", False), page.run_thread(page.update)),
            ffmpeg_path[0])
    pv_dl.on_click = on_pv_dl
    pv_open.on_click = lambda e: open_folder(pv_path.value.strip())

    # ══════════════════════════════════════════════
    #  TAB AUDIO
    # ══════════════════════════════════════════════
    aud_url  = make_url_field("Link para converter em MP3...")
    aud_path = make_path_field("Salvar áudio em")
    pick_aud = ft.IconButton(ft.Icons.FOLDER_OPEN, on_click=lambda _: open_picker(aud_path), tooltip="Alterar pasta")
    
    aud_prog = ft.ProgressBar(value=0, color=ACCENT, bgcolor="#eeeeee", height=8)
    aud_stat = ft.Text("", color=TEXT_SECONDARY, size=12)
    aud_dl   = LabelButton("🎵 Baixar MP3")
    aud_open = LabelButton("📂 Abrir Pasta", primary=False, icon=ft.Icons.FOLDER_OPEN)

    async def on_aud_dl(e):
        url, folder = aud_url.value.strip(), aud_path.value.strip()
        if not url: await snack("Link vazio!", ERROR_COLOR); return
        if not os.path.exists(folder): os.makedirs(folder, exist_ok=True)
        aud_dl.disabled = True
        aud_prog.value = 0
        page.update()
        
        downloader.download_audio(url, folder, 
            lambda p,s,eta: (setattr(aud_prog, "value", p/100), setattr(aud_stat, "value", f"{p:.1f}% | {s}"), page.run_thread(page.update)),
            lambda m: (page.run_task(snack, m), setattr(aud_dl, "disabled", False), page.run_thread(page.update)),
            lambda m: (page.run_task(snack, m, ERROR_COLOR), setattr(aud_dl, "disabled", False), page.run_thread(page.update)),
            ffmpeg_path[0])
    aud_dl.on_click = on_aud_dl
    aud_open.on_click = lambda e: open_folder(aud_path.value.strip())

    # ══════════════════════════════════════════════
    #  LAYOUT
    # ══════════════════════════════════════════════
    def card(title, controls):
        return ft.Container(
            content=ft.Column([
                ft.Text(title, weight="bold", size=18, color=TEXT_PRIMARY),
                ft.Divider(color=BORDER, height=1),
                *controls
            ], spacing=15),
            bgcolor=SURFACE, padding=25, border_radius=15,
            border=ft.Border.all(1, BORDER),
            shadow=ft.BoxShadow(blur_radius=10, color="#0000000a"),
        )

    tab_v_view = ft.Container(
        content=ft.Column([
            card("Vídeo Único", [
                ft.Row([vid_url, fetch_btn.ctrl], spacing=10),
                vid_drop, 
                ft.Row([vid_path, pick_v_btn], spacing=10), 
                vid_prog, vid_stat,
                ft.Row([dl_btn.ctrl, open_btn.ctrl], spacing=10),
            ]),
            gap(20),
            card("Playlist de Vídeos", [
                pv_url, 
                ft.Row([pv_path, pick_pv], spacing=10),
                pv_prog, pv_stat,
                ft.Row([pv_dl.ctrl, pv_open.ctrl], spacing=10),
            ])
        ], scroll=ft.ScrollMode.AUTO),
        padding=20, expand=True
    )

    tab_a_view = ft.Container(
        content=ft.Column([
            card("Áudio MP3", [
                aud_url, 
                ft.Row([aud_path, pick_aud], spacing=10),
                aud_prog, aud_stat,
                ft.Row([aud_dl.ctrl, aud_open.ctrl], spacing=10),
            ])
        ], scroll=ft.ScrollMode.AUTO),
        padding=20, expand=True
    )

    # ── Flet 0.82+ Tab Navigation ────────────────
    tab_bar = ft.TabBar(
        tabs=[
            ft.Tab(label="🎬 VÍDEOS"),
            ft.Tab(label="🎵 ÁUDIO"),
        ],
    )
    
    tab_view_container = ft.TabBarView(
        controls=[tab_v_view, tab_a_view],
        expand=True
    )

    tabs_control = ft.Tabs(
        length=2,
        content=ft.Column([
            tab_bar,
            tab_view_container
        ], expand=True),
        expand=True
    )

    banner = ft.Container(
        content=ft.Row([
            ft.Icon(ft.Icons.WARNING, color="orange"),
            ft.Text("FFmpeg não encontrado! Algumas qualidades podem falhar.", color=TEXT_PRIMARY, expand=True),
        ]),
        bgcolor="#fff4e5", padding=15, border_radius=10, 
        visible=not has_ffmpeg, margin=ft.Margin(20, 10, 20, 0)
    )

    header = ft.Container(
        content=ft.Row([
            ft.Icon(ft.Icons.PLAY_CIRCLE_FILL, color=ACCENT, size=40),
            ft.Text("YT Downloader Pro", size=24, weight="bold", color=TEXT_PRIMARY),
        ]),
        padding=ft.Padding(25, 20, 25, 10), bgcolor=SURFACE, border=ft.Border(bottom=ft.BorderSide(1, BORDER))
    )

    page.add(header, banner, tabs_control)


if __name__ == "__main__":
    # Standard entry point
    ft.run(main)
