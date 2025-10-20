import edge_tts
import json
import asyncio
import os
import subprocess
from pydub import AudioSegment

#opening json file
with open('assets/post_data.json') as json_file:
    json_todict = json.loads(json_file.read())

#tranfering every part of json file in to a list and generatin a single audio file
def single_file():
    post_data_list = []
    post_data_list.append(json_todict['title'])
    post_data_list.append(" ... ")
    post_data_list.append(json_todict['body'])
    post_data_list.append(" ... ")
    for comment in json_todict['comments']:
        post_data_list.append(comment)
        post_data_list.append(" ... ")


    async def generate_speech(strings, output_file="assets/output.mp3"):
        text = "".join(strings)  # each "..." acts as a small pause
        voice = "en-US-GuyNeural"
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_file)

    title_data = []
    title_data.append(json_todict['title'])
    async def genenerate_title_audio(strings, output_file="assets/title_output.mp3"):
        text = "".join(strings)
        voice = "en-US-GuyNeural"
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_file)
    


    asyncio.run(generate_speech(post_data_list))
    print("Speech generated successfully!")
    asyncio.run(genenerate_title_audio(title_data))
    print("title audio generated succesufully!")

    print("Generating word-level subtitles with Whisper...")
    subprocess.run([
        "whisper",
        "assets/output.mp3",
        "--model", "base",
        "--output_format", "json",
        "--output_dir", "assets",
        "--word_timestamps", "True"
    ])
    print("Word-level subtitles generated!")

#tranfering every part of json file in to a list and generating multiple audio files
def multiple_files():
    """
    Generates separate audio files for title, body, and comments,
    adds natural pauses between sections, and concatenates them into output.mp3
    """
    # Create output directory if it doesn't exist
    output_dir = "assets/audio"
    os.makedirs(output_dir, exist_ok=True)
    
    # Prepare data structure with labels
    post_data_list = [
        ("title", json_todict["title"]),
        ("body", json_todict["body"])
    ]

    for i, comment in enumerate(json_todict["comments"], start=1):
        post_data_list.append((f"comment_{i}", comment))
    
    async def generate_speech(strings, output_dir="assets/audio"):
        """Generate individual audio files for each section"""
        audio_files = []
        for label, text in strings:
            voice = "en-US-GuyNeural"
            filename = os.path.join(output_dir, f"{label}.mp3")
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(filename)
            audio_files.append(filename)
            print(f"Generated: {filename}")

        return audio_files
    
    # Generate all audio files
    audio_files = asyncio.run(generate_speech(post_data_list, output_dir))
    print("\nAll audio files generated successfully!")
    
    # Create natural pauses (1.5 seconds of silence)
    pause_duration_ms = 1500  # 1.5 seconds
    silence = AudioSegment.silent(duration=pause_duration_ms)
    
    # Concatenate audio files with pauses
    print("\nConcatenating audio files with natural pauses...")
    combined = AudioSegment.empty()
    
    for i, audio_file in enumerate(audio_files):
        # Load the audio segment
        segment = AudioSegment.from_mp3(audio_file)
        combined += segment
        
        # Add pause after each segment except the last one
        if i < len(audio_files) - 1:
            combined += silence
            print(f"Added pause after {os.path.basename(audio_file)}")
    
    # Export the final combined audio
    output_path = "assets/output.mp3"
    combined.export(output_path, format="mp3")
    print(f"\nFinal audio exported to: {output_path}")
    
    # Generate title-only audio for video overlay
    title_data = [("title", json_todict['title'])]
    asyncio.run(generate_speech(title_data, "assets"))
    # Rename to title_output.mp3 for compatibility
    if os.path.exists("assets/title.mp3"):
        os.rename("assets/title.mp3", "assets/title_output.mp3")
    print("Title audio generated successfully!")
    
    # Generate word-level subtitles using Whisper
    print("\nGenerating word-level subtitles with Whisper...")
    subprocess.run([
        "whisper",
        output_path,
        "--model", "base",
        "--output_format", "json",
        "--output_dir", "assets",
        "--word_timestamps", "True"
    ])
    print("Word-level subtitles generated!")

    


#print(json_todict)

#print(post_data_list)

if __name__ == "__main__":
    multiple_files()