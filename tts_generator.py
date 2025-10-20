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


    asyncio.run(generate_speech(post_data_list))
    print("Speech generated successfully!")

    print("Generating subtitles with Whisper...")
    subprocess.run([
        "whisper",
        "assets/output.mp3",
        "--model", "base",
        "--output_format", "srt",
        "--output_dir", "assets"
    ])
    print("Subtitles generated!")

#tranfering every part of json file in to a list and generating multiple audio files
def multiple_files():
    post_data_list =[
        ("title", json_todict["title"]),
        ("body", json_todict["body"])
    ]

    for i, comment in enumerate(json_todict["comments"], start=1):
        post_data_list.append((f"comment_{i}",comment))
    
    async def generate_speech(strings, output_dir="assets/audio"):
        audio_files = []
        for label, text in strings:
            voice = "en-US-GuyNeural"
            filename = os.path.join(output_dir, f"{label}.mp3")
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(filename)
            audio_files.append(filename)
            print(f"Generated: {filename}")

        return audio_files
    
    audio_files = asyncio.run(generate_speech(post_data_list))
    print("\nAll audio files generated in order:")
    print(audio_files)
    


#print(json_todict)

#print(post_data_list)

if __name__ == "__main__":
    #multiple_files()
    single_file()