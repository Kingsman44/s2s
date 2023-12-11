import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi
import json
from moviepy.editor import AudioFileClip
import os
import shutil
import pandas as pd

AUDIO_WEBM_PATH="audio_webm"
TRANSCRIPT_PATH="transcript"
AUDIO_PATH="audio"

if not os.path.exists(AUDIO_WEBM_PATH):
    os.makedirs(AUDIO_WEBM_PATH)

if not os.path.exists(TRANSCRIPT_PATH):
    os.makedirs(TRANSCRIPT_PATH)

if not os.path.exists(AUDIO_PATH):
    os.makedirs(AUDIO_PATH)    

with open('dataset.txt', 'r') as file:
    yt_ids = [line.strip() for line in file.readlines()]
    
yt_links = [f"https://youtu.be/{ids}" for ids in yt_ids]

ydl = yt_dlp.YoutubeDL({
    'format': 'ba[language=hi],bestaudio',
    'audio-multistreams': True,
    'outtmpl': os.path.join(AUDIO_WEBM_PATH,'%(id)s.%(language)s.%(ext)s')
})

for i in range(len(yt_links)): 
    file_path = os.path.join(AUDIO_WEBM_PATH, yt_ids[i]+'.hi.webm')
    new_file_path = os.path.join(AUDIO_WEBM_PATH, yt_ids[i]+'.en.webm')
    us_file_path = os.path.join(AUDIO_WEBM_PATH, yt_ids[i]+'.en-US.webm')
    if not os.path.exists(file_path):
        ydl.download([yt_links[i]])
    else:
        print(f"Skipping download for {file_path} as it already exists.")
    
    # After download, check and rename the file if needed
    if os.path.exists(us_file_path):
        os.rename(us_file_path, new_file_path)
        print(f"Renamed file: {us_file_path} to {new_file_path}")

for ids in yt_ids:
    for lang in ['en','hi']:
        trans = YouTubeTranscriptApi.get_transcript(ids, languages=[lang])
        with open(os.path.join(TRANSCRIPT_PATH,ids+'.'+lang+'.json'), 'w', encoding='utf-8') as json_file:
            json.dump(trans, json_file, ensure_ascii=False, indent=2)


        input_file = os.path.join(AUDIO_WEBM_PATH,ids+'.'+lang+'.webm')
        output_file = os.path.join(AUDIO_PATH,ids+'.'+lang+'.wav')
        if os.path.exists(input_file) and not os.path.exists(output_file):
            audio_clip = AudioFileClip(input_file)
            audio_clip.write_audiofile(output_file, codec='pcm_s16le', fps=16000)

shutil.rmtree(AUDIO_WEBM_PATH)

df = pd.DataFrame({'File': yt_ids})
df.to_csv('data.csv', index=False)
print("DONE")