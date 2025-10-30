import subprocess
import moviepy.editor as mp
import os

def fast_tiktok_render(
    video_path,
    audio_path,
    subtitle_path="assets/dynamic_subs.ass",
    output_path="tiktok_fast.mp4",
    screenshot_path="assets/screenshots/new.png",
    #title_audio_path="assets/title_output.mp3"
    title_audio_path="assets/audio/title.mp3"
):
    # Load durations
    audio = mp.AudioFileClip(audio_path)
    audio_title = mp.AudioFileClip(title_audio_path)
    video = mp.VideoFileClip(video_path)

    total_length = audio.duration
    trim_length = min(video.duration, total_length)
    title_length = audio_title.duration

    trimmed_path = "trimmed.mp4"
    with_audio = "combined.mp4"

    # Trim video fast (no re-encode)
    subprocess.run([
        "ffmpeg", "-y", "-i", video_path,
        "-t", str(trim_length),
        "-an", "-c", "copy", trimmed_path
    ], check=True)

    # Combine trimmed video + main audio (no video re-encode)
    subprocess.run([
        "ffmpeg", "-y", "-i", trimmed_path, "-i", audio_path,
        "-map", "0:v", "-map", "1:a",
        "-c:v", "copy", "-c:a", "aac",
        "-shortest",
        with_audio
    ], check=True)

    # Apply subtitles + overlay image (only one encoding step)
    subtitle_path_escaped = subtitle_path.replace("\\", "/").replace(":", "\\:")
    screenshot_path_escaped = screenshot_path.replace("\\", "/")

    # Build a single FFmpeg filter chain
    vf_filter = (
        f"[0:v]ass={subtitle_path_escaped}[v];"
        f"movie={screenshot_path_escaped}[overlay];"
        f"[v][overlay]overlay=(main_w-overlay_w)/2:(main_h-overlay_h)/2:"
        f"enable='lte(t,{title_length})'"
    )

    # Render final output (single encode)
    subprocess.run([
        "ffmpeg", "-y", "-i", with_audio,
        "-filter_complex", vf_filter,
        "-c:v", "libx264", "-preset", "ultrafast",  #  fastest possible encoding
        "-crf", "23",  # trade-off between speed and quality
        "-c:a", "aac",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",  # helps with TikTok upload compatibility
        output_path
    ], check=True)

    # Cleanup
    for f in [trimmed_path, with_audio]:
        if os.path.exists(f):
            os.remove(f)

    print(f"Fast TikTok render complete: {output_path} (subtitles re-burned, overlay first {title_length:.2f}s)")


if __name__ == "__main__":
    from create_dynamic_subtitles import create_karaoke_subtitles

    # Subtitles are generated dynamically each time
    create_karaoke_subtitles("assets/output.json", "assets/dynamic_subs.ass")

    fast_tiktok_render(
        "assets/video_tiktok.mp4",  # Pre-cropped TikTok video
        "assets/output.mp3",
        "assets/dynamic_subs.ass",
        "tiktok_fast.mp4",
        "assets/screenshots/new.png"
    )
