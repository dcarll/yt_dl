"""
downloader.py — yt-dlp wrapper for YouTube Downloader app
"""
import threading
import yt_dlp


def fetch_formats(url: str) -> list[dict]:
    """
    Fetch available video+audio formats for a YouTube URL.
    Returns a list of dicts: {format_id, resolution, ext, note}
    """
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        "noplaylist": True,
        "check_formats": False,
        "socket_timeout": 5,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
    
    formats = []
    seen = set()

    for f in info.get("formats", []):
        # Only keep formats that have both video and reasonable quality
        vcodec = f.get("vcodec", "none")
        acodec = f.get("acodec", "none")
        height = f.get("height")
        ext = f.get("ext", "?")
        format_id = f.get("format_id", "")

        if vcodec == "none" or not height:
            continue

        key = (height, ext)
        if key in seen:
            continue
        seen.add(key)

        note = f.get("format_note", "")
        fps = f.get("fps", "")
        label = f"{height}p"
        if fps:
            label += f" {fps}fps"
        if note:
            label += f" ({note})"
        label += f" · {ext.upper()}"

        formats.append({
            "format_id": format_id,
            "label": label,
            "height": height,
            "ext": ext,
        })

    # Sort highest quality first
    formats.sort(key=lambda x: x["height"], reverse=True)
    return formats


def _make_progress_hook(callback):
    """Create a yt-dlp progress hook that calls callback(percent, speed, eta, status)."""
    def hook(d):
        if d["status"] == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate", 0)
            downloaded = d.get("downloaded_bytes", 0)
            percent = (downloaded / total * 100) if total else 0
            speed = d.get("_speed_str", "")
            eta = d.get("_eta_str", "")
            callback(percent, speed, eta, "downloading")
        elif d["status"] == "finished":
            callback(100, "", "", "finished")
        elif d["status"] == "error":
            callback(0, "", "", "error")
    return hook


def download_video(url: str, format_id: str, output_path: str, progress_cb, done_cb, error_cb, ffmpeg_path=None):
    """
    Download a single YouTube video with the given format_id.
    Runs in a background thread.
    """
    def run():
        try:
            ydl_opts = {
                "format": f"{format_id}+bestaudio/best[height<={format_id}]/{format_id}",
                "outtmpl": f"{output_path}/%(title)s.%(ext)s",
                "merge_output_format": "mp4",
                "quiet": True,
                "no_warnings": True,
                "noplaylist": True,
                "check_formats": False,
                "socket_timeout": 5,
                "progress_hooks": [_make_progress_hook(lambda p, s, e, st: progress_cb(p, s, e))],
            }
            if ffmpeg_path:
                ydl_opts["ffmpeg_location"] = ffmpeg_path
                
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            done_cb("Download concluído!")
        except Exception as ex:
            error_cb(str(ex))

    threading.Thread(target=run, daemon=True).start()


def download_audio(url: str, output_path: str, progress_cb, done_cb, error_cb, ffmpeg_path=None):
    """
    Download a YouTube video as MP3.
    """
    def run():
        try:
            ydl_opts = {
                "format": "bestaudio/best",
                "outtmpl": f"{output_path}/%(title)s.%(ext)s",
                "postprocessors": [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }],
                "quiet": True,
                "no_warnings": True,
                "noplaylist": True,
                "check_formats": False,
                "socket_timeout": 5,
                "progress_hooks": [_make_progress_hook(lambda p, s, e, st: progress_cb(p, s, e))],
            }
            if ffmpeg_path:
                ydl_opts["ffmpeg_location"] = ffmpeg_path

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            done_cb("Download de áudio concluído!")
        except Exception as ex:
            error_cb(str(ex))

    threading.Thread(target=run, daemon=True).start()


def download_playlist_video(url: str, format_spec: str, output_path: str, progress_cb, done_cb, error_cb, ffmpeg_path=None):
    """Download all videos in a playlist."""
    def run():
        try:
            ydl_opts = {
                "format": format_spec,
                "outtmpl": f"{output_path}/%(playlist_index)s - %(title)s.%(ext)s",
                "merge_output_format": "mp4",
                "quiet": True,
                "no_warnings": True,
                "check_formats": False,
                "socket_timeout": 5,
                "progress_hooks": [_make_progress_hook(lambda p, s, e, st: progress_cb(p, s, e))],
                "ignoreerrors": True,
            }
            if ffmpeg_path:
                ydl_opts["ffmpeg_location"] = ffmpeg_path

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            done_cb("Download da playlist concluído!")
        except Exception as ex:
            error_cb(str(ex))

    threading.Thread(target=run, daemon=True).start()


def download_playlist_audio(url: str, output_path: str, progress_cb, done_cb, error_cb, ffmpeg_path=None):
    """Download all videos in a playlist as MP3."""
    def run():
        try:
            ydl_opts = {
                "format": "bestaudio/best",
                "outtmpl": f"{output_path}/%(playlist_index)s - %(title)s.%(ext)s",
                "postprocessors": [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }],
                "quiet": True,
                "no_warnings": True,
                "check_formats": False,
                "socket_timeout": 5,
                "progress_hooks": [_make_progress_hook(lambda p, s, e, st: progress_cb(p, s, e))],
                "ignoreerrors": True,
            }
            if ffmpeg_path:
                ydl_opts["ffmpeg_location"] = ffmpeg_path

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            done_cb("Download da playlist de áudio concluído!")
        except Exception as ex:
            error_cb(str(ex))

    threading.Thread(target=run, daemon=True).start()
