# Reddit Stories Video Generator

A Python tool that automatically generates TikTok-style videos with captions and text-to-speech from Reddit posts.

## Description

This project fetches Reddit posts and creates engaging short-form videos perfect for TikTok, complete with automated captions and AI-generated voiceovers.

## Prerequisites

- Python 3.11
- FFmpeg (for video processing)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Rapolas03/reddit-stories-video-generator.git
cd reddit-stories-video-generator
```

2. Install the required Python packages:
```bash
pip install -r requirements.txt
```

### Dependencies

The project uses the following Python packages:
- `moviepy==1.0.3` - Video editing and processing
- `praw` - Reddit API wrapper
- `python-dotenv` - Environment variable management
- `pick` - Interactive selection in CLI
- `edge-tts` - Text-to-speech generation
- `openai-whisper` - Audio transcription
- `numpy<2` - Required for compatibility with moviepy

**Note:** NumPy version must be less than 2.0 for compatibility with moviepy.

## Setup

### 1. Prepare Background Video

Before running the script, you need to prepare a background video:

1. Download your desired background video
2. Save it as `video.mp4` in the `assets` folder
3. Format the video for TikTok (9:16 aspect ratio) using FFmpeg:

```bash
ffmpeg -i assets/video.mp4 \
-vf "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920" \
-c:v libx264 -crf 18 -preset veryfast \
-c:a copy \
assets/video_tiktok.mp4
```

This command will:
- Scale and crop the video to 1080x1920 (TikTok format)
- Maintain high quality (CRF 18)
- Process quickly (veryfast preset)
- Keep the original audio

### 2. Configure Reddit API

Create a `.env` file in the project root with your Reddit API credentials:
```
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USER_AGENT=your_user_agent
```

## Usage

Run the main script:
```bash
python main.py
```

Follow the interactive prompts to select your Reddit source and generate your video.

## Project Structure

```
reddit-stories-video-generator/
├── assets/
│   ├── video.mp4           # Original background video
│   └── video_tiktok.mp4    # Formatted TikTok video
├── requirements.txt
└── [Python scripts]
```

## License

This project is available for use under standard open-source terms.

## Contributing

Contributions, issues, and feature requests are welcome!