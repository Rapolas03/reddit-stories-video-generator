import whisper

model = whisper.load_model("base")
result = model.transcribe("assets/output.mp3")

print(result["text"])


