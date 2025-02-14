
from pydub import AudioSegment
import wave
import json
from vosk import Model, KaldiRecognizer
import os

def download_audio(url):
    # yt = YouTube(url)
    # audio_stream = yt.streams.filter(only_audio=True).first()
    # audio_file = audio_stream.download(filename="video_audio.mp4")
    mp3_filename = "audio.mp3"
    print("downloaded")
    # print(audio_file)
    audio = AudioSegment.from_file('video_audio.mp4', format="mp4")
    audio.export(mp3_filename, format="mp3")
    print("converted")

    # Remove the MP4 file after conversion
    # os.remove(audio_file)

    return mp3_filename