import subprocess
import moviepy.editor as mp
import os

def fast_tiktok_render(video_path, audio_path, subtitle_path="assets/dynamic_subs.ass", output_path="tiktok_fast.mp4"):
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

    # --- 3️⃣ Crop, resize for TikTok & add dynamic word-by-word subtitles ---
    if os.path.exists(subtitle_path):
        # Escape the subtitle path for FFmpeg
        subtitle_path_escaped = subtitle_path.replace('\\', '/').replace(':', '\\:')
        
        vf_filter = f"crop=in_h*9/16:in_h:(in_w-in_h*9/16)/2:0,scale=1080:1920,ass={subtitle_path_escaped}"
    else:
        print(f"⚠️ Warning: Subtitle file not found at {subtitle_path}. Proceeding without subtitles.")
        vf_filter = "crop=in_h*9/16:in_h:(in_w-in_h*9/16)/2:0,scale=1080:1920"
    
    subprocess.run([
        "ffmpeg", "-y", "-i", with_audio,
        "-vf", vf_filter,
        "-c:v", "libx264", "-c:a", "aac",
        output_path
    ], check=True)

    # --- 4️⃣ Cleanup ---
    for f in [trimmed_path, with_audio]:
        if os.path.exists(f):
            os.remove(f)

    print(f"✅ TikTok video with dynamic word-highlighting subtitles ready: {output_path}")


if __name__ == "__main__":
    # First create the dynamic subtitles from Whisper JSON
    from create_dynamic_subtitles import create_karaoke_subtitles
    create_karaoke_subtitles("assets/output.json", "assets/dynamic_subs.ass")
    
    # Then render the video
    fast_tiktok_render("assets/video.mp4", "assets/output.mp3", "assets/dynamic_subs.ass")