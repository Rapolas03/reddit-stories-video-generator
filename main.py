"""
Main script to generate TikTok videos from Reddit posts
Orchestrates all the individual scripts in the correct order
"""

import os
import json
from reddit_fetcher import extractpost
from screenshot_reddit import RedditPostImage
from tts_generator import single_file, multiple_files
from create_dynamic_subtitles import create_karaoke_subtitles
from video_generator import fast_tiktok_render

def main():
    print("=" * 60)
    print("Reddit Stories Video Generator")
    print("=" * 60)
    
    # Step 1: Fetch Reddit post data
    print("\n[Step 1/5] Fetching Reddit post...")
    extractpost()
    
    # Step 2: Generate screenshot from post data
    print("\n[Step 2/5] Generating Reddit post screenshot...")
    with open('assets/post_data.json', 'r', encoding='utf-8') as f:
        post_data = json.load(f)
    
    reddit_img = RedditPostImage()
    screenshot_path = reddit_img.create_post_image(
        title=post_data['title'],
        subreddit=post_data['subreddit']
    )
    print(f"Screenshot saved to: {screenshot_path}")
    
    # Step 3: Generate TTS audio
    print("\n[Step 3/5] Generating text-to-speech audio...")
    multiple_files()
    
    # Step 4: Create dynamic subtitles
    print("\n[Step 4/5] Creating word-level subtitles...")
    create_karaoke_subtitles("assets/output.json", "assets/dynamic_subs.ass")
    
    # Step 5: Generate final video
    print("\n[Step 5/5] Rendering final TikTok video...")
    
    # Check if video file exists
    video_path = "assets/video.mp4"
    if not os.path.exists(video_path):
        print(f" Warning: Background video not found at {video_path}")
        print("Please add a background video to assets/video.mp4")
        return
    
    fast_tiktok_render(
        video_path=video_path,
        audio_path="assets/output.mp3",
        subtitle_path="assets/dynamic_subs.ass",
        output_path="tiktok_final.mp4",
        screenshot_path="assets/screenshots/new.png"
    )
    
    print("\n" + "=" * 60)
    print("Video generation complete!")
    print("Output file: tiktok_final.mp4")
    print("=" * 60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nProcess interrupted by user")
    except Exception as e:
        print(f"\n\n Error occurred: {e}")
        raise