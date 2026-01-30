
import edge_tts
import json
import asyncio
import os
import subprocess

#opening json file
with open('assets/post_data.json') as json_file:
    json_todict = json.loads(json_file.read())

#tranfering every part of json file in to a list and generatin a single audio file
def single_file():
    post_data_list = []
    post_data_list.append(json_todict['title'])
    post_data_list.append(" ... ")
    
    # Only add body if it's not empty
    if json_todict.get('body') and json_todict['body'].strip():
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
def multiple_files(clean_temp=False):
    import shutil
    output_dir = "assets/audio"
    os.makedirs(output_dir, exist_ok=True)

    post_data_list = [
        ("title", json_todict["title"]),
    ]
    
    # Only add body if it's not empty
    if json_todict.get("body") and json_todict["body"].strip():
        post_data_list.append(("body", json_todict["body"]))
    
    for i, comment in enumerate(json_todict["comments"], start=1):
        post_data_list.append((f"comment_{i}", comment))

    async def generate_speech(strings, output_dir=output_dir):
        audio_files = []
        for label, text in strings:
            # Skip empty texts
            if not text or not text.strip():
                print(f"Skipping empty text for {label}")
                continue
                
            voice = "en-US-GuyNeural"
            filename = os.path.join(output_dir, f"{label}.mp3")
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(filename)
            audio_files.append(filename)
            print(f"Generated: {filename}")
        return audio_files

    # generate individual audio files
    audio_files = asyncio.run(generate_speech(post_data_list))
    print("\nAll audio files generated in order:")
    print(audio_files)

    #1.5s silence file WITH matching audio params
    silence_file = os.path.join(output_dir, "silence_1_5s.mp3")
    
    subprocess.run([
        "ffmpeg", "-f", "lavfi", "-i", "anullsrc=channel_layout=mono:sample_rate=44100",
        "-t", "1.5", "-acodec", "libmp3lame", "-q:a", "5", "-y", silence_file
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    #concat list
    concat_list_path = os.path.join(output_dir, "concat_list.txt")
    with open(concat_list_path, "w", encoding="utf-8") as f:
        for i, file in enumerate(audio_files):
            f.write(f"file '{os.path.abspath(file)}'\n")
            # add silence after each file except the last
            if i != len(audio_files) - 1:
                f.write(f"file '{os.path.abspath(silence_file)}'\n")

    # merge and RE-ENCODE, nu nes krc kitaip neveikia
    merged_output = "assets/output.mp3"
    subprocess.run([
        "ffmpeg", "-f", "concat", "-safe", "0",
        "-i", concat_list_path,
        "-acodec", "libmp3lame", "-ar", "44100", "-ac", "1",
        "-q:a", "2", "-y", merged_output
    ], check=True)

    print(f"Merged audio created at: {merged_output}")

    # Whisper word-level subtitles (json)
    print("Generating word-level subtitles with Whisper...")
    subprocess.run([
        "whisper",
        merged_output,
        "--model", "base",
        "--output_format", "json",
        "--output_dir", "assets",
        "--word_timestamps", "True"
    ], check=True)
    print("Word-level subtitles generated!")

    # cleanup of temps
    if clean_temp:
        try:
            # remove individual audio files and list & silence file
            for fpath in audio_files:
                if os.path.exists(fpath):
                    os.remove(fpath)
            if os.path.exists(silence_file):
                os.remove(silence_file)
            if os.path.exists(concat_list_path):
                os.remove(concat_list_path)
            print("Temporary files cleaned up.")
        except Exception as e:
            print("Cleanup error:", e)

#print(json_todict)

#print(post_data_list)

if __name__ == "__main__":
    multiple_files()
    #single_file()
