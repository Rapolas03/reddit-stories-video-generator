import edge_tts
import json
import asyncio

#opening json file
with open('assets/post_data.json') as json_file:
    json_todict = json.loads(json_file.read())

#tranfering every part of json file in to a list 
post_data_list = []
post_data_list.append(json_todict['title'])
post_data_list.append(json_todict['body'])
for comment in json_todict['comments']:
    post_data_list.append(comment)


async def generate_speech(strings, output_file="assets/output.mp3"):
    text = "   ".join(strings)
    voice = "en-US-GuyNeural"  # Regural guy voice (might change later)
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_file)


asyncio.run(generate_speech(post_data_list))
print("Speech generated successfully!")

#print(json_todict)

#print(post_data_list)