import subprocess
import moviepy.editor as mp
import os

def fast_tiktok_render(video_path, audio_path, output_path="tiktok_fast.mp4"):
    # Load media to calculate durations
    audio = mp.AudioFileClip(audio_path)
    video = mp.VideoFileClip(video_path)
    total_length = audio.duration
    trim_length = min(video.duration, total_length)

    trimmed_path = "trimmed.mp4"
    with_audio = "combined.mp4"

    # --- 1️⃣ Trim video fast (no re-encode) ---
    subprocess.run([
        "ffmpeg", "-y", "-i", video_path,
        "-t", str(trim_length),
        "-an", "-c", "copy", trimmed_path
    ], check=True)

    # --- 2️⃣ Combine trimmed video + audio ---
    subprocess.run([
        "ffmpeg", "-y", "-i", trimmed_path, "-i", audio_path,
        "-map", "0:v", "-map", "1:a",
        "-c:v", "copy", "-c:a", "aac",
        "-shortest",
        with_audio
    ], check=True)

    # --- 3️⃣ Crop & resize for TikTok (final re-encode) ---
    subprocess.run([
        "ffmpeg", "-y", "-i", with_audio,
        "-vf", "crop=in_h*9/16:in_h:(in_w-in_h*9/16)/2:0,scale=1080:1920",
        "-c:v", "libx264", "-c:a", "aac",
        output_path
    ], check=True)

    # --- 4️⃣ Cleanup ---
    for f in [trimmed_path, with_audio]:
        if os.path.exists(f):
            os.remove(f)

    print(f"✅ TikTok video ready: {output_path}")


if __name__ == "__main__":
    fast_tiktok_render("assets/video.mp4", "assets/output.mp3")
