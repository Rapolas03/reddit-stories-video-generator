import subprocess
import moviepy.editor as mp
import os

def fast_tiktok_render(
    video_path,
    audio_path,
    subtitle_path="assets/dynamic_subs.ass",
    output_path="tiktok_fast.mp4",
    screenshot_path="assets/screenshots/new.png"
):
    # Load media to calculate durations
    audio = mp.AudioFileClip(audio_path)
    audio_title = mp.AudioFileClip("assets/title_output.mp3")
    video = mp.VideoFileClip(video_path)
    total_length = audio.duration
    trim_length = min(video.duration, total_length)
    title_length = audio_title.duration

    trimmed_path = "trimmed.mp4"
    with_audio = "combined.mp4"

    # --- 1️⃣ Trim video fast (no re-encode) ---
    subprocess.run([
        "ffmpeg", "-y", "-i", video_path,
        "-t", str(trim_length),
        "-an", "-c", "copy", trimmed_path
    ], check=True)

    # --- 2️⃣ Combine trimmed video + main audio ---
    subprocess.run([
        "ffmpeg", "-y", "-i", trimmed_path, "-i", audio_path,
        "-map", "0:v", "-map", "1:a",
        "-c:v", "copy", "-c:a", "aac",
        "-shortest",
        with_audio
    ], check=True)

    # --- 3️⃣ Crop, resize, add subtitles, and overlay screenshot ---
    if os.path.exists(subtitle_path):
        subtitle_path_escaped = subtitle_path.replace('\\', '/').replace(':', '\\:')
        base_filter = f"crop=in_h*9/16:in_h:(in_w-in_h*9/16)/2:0,scale=1080:1920,ass={subtitle_path_escaped}"
    else:
        print(f"⚠️ Warning: Subtitle file not found at {subtitle_path}. Proceeding without subtitles.")
        base_filter = "crop=in_h*9/16:in_h:(in_w-in_h*9/16)/2:0,scale=1080:1920"

    # --- 🆕 Add overlay image on top for first title_length seconds ---
    # Centered overlay: (main_w-overlay_w)/2 horizontally, (main_h-overlay_h)/2 vertically
    screenshot_path_escaped = screenshot_path.replace("\\", "/")
    vf_filter = (
        f"[0:v]{base_filter}[v];"
        f"movie={screenshot_path_escaped}[overlay];"
        f"[v][overlay]overlay=(main_w-overlay_w)/2:(main_h-overlay_h)/2:enable='lte(t,{title_length})'"
    )

    subprocess.run([
        "ffmpeg", "-y", "-i", with_audio,
        "-filter_complex", vf_filter,
        "-c:v", "libx264", "-c:a", "aac",
        "-pix_fmt", "yuv420p",
        output_path
    ], check=True)

    # --- 4️⃣ Cleanup ---
    for f in [trimmed_path, with_audio]:
        if os.path.exists(f):
            os.remove(f)

    print(f"✅ TikTok video with centered screenshot overlay (first {title_length:.2f}s) ready: {output_path}")


if __name__ == "__main__":
    from create_dynamic_subtitles import create_karaoke_subtitles
    create_karaoke_subtitles("assets/output.json", "assets/dynamic_subs.ass")
    
    fast_tiktok_render(
        "assets/video.mp4",
        "assets/output.mp3",
        "assets/dynamic_subs.ass",
        "tiktok_fast.mp4",
        "assets/screenshots/new.png"
    )
