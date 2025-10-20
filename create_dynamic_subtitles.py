import json
import subprocess
import os

def create_karaoke_subtitles(whisper_json_path, output_ass_path="assets/dynamic_subs.ass"):
    """
    Creates ASS subtitle file with word-by-word karaoke effect
    """
    
    # Load Whisper JSON
    with open(whisper_json_path, 'r', encoding='utf-8') as f:
        whisper_data = json.load(f)
    
    # ASS file header
    ass_content = """[Script Info]
Title: Dynamic Subtitles
ScriptType: v4.00+
WrapStyle: 0
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,70,&H00FFFFFF,&H00FFFF00,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,3,2,2,50,50,350,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    
    # Process segments and words
    for segment in whisper_data.get('segments', []):
        words = segment.get('words', [])
        
        if not words:
            continue
        
        # Group words into phrases (max 6 words per line)
        max_words_per_line = 6
        phrases = []
        current_phrase = []
        
        for word in words:
            current_phrase.append(word)
            if len(current_phrase) >= max_words_per_line:
                phrases.append(current_phrase)
                current_phrase = []
        
        if current_phrase:
            phrases.append(current_phrase)
        
        # Create ASS dialogue lines with karaoke effect
        for phrase in phrases:
            phrase_start = phrase[0]['start']
            phrase_end = phrase[-1]['end']
            
            # Format timestamps for ASS (H:MM:SS.CS)
            start_time = format_ass_time(phrase_start)
            end_time = format_ass_time(phrase_end)
            
            # Build karaoke tags for each word
            karaoke_text = ""
            for word_data in phrase:
                word_text = word_data['word'].strip()
                # Calculate duration in centiseconds
                duration_cs = int((word_data['end'] - word_data['start']) * 100)
                # Add karaoke tag: \k<duration> changes color for that duration
                karaoke_text += f"{{\\k{duration_cs}}}{word_text} "
            
            # Add dialogue line
            ass_content += f"Dialogue: 0,{start_time},{end_time},Default,,0,0,0,,{karaoke_text.strip()}\n"
    
    # Write ASS file
    with open(output_ass_path, 'w', encoding='utf-8') as f:
        f.write(ass_content)
    
    print(f"✅ Dynamic ASS subtitles created: {output_ass_path}")
    return output_ass_path


def format_ass_time(seconds):
    """Convert seconds to ASS time format H:MM:SS.CS"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    centiseconds = int((seconds % 1) * 100)
    return f"{hours}:{minutes:02d}:{secs:02d}.{centiseconds:02d}"


if __name__ == "__main__":
    create_karaoke_subtitles("assets/output.json", "assets/dynamic_subs.ass")