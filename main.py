from pytubefix import YouTube
from pytube.exceptions import VideoUnavailable
from pytubefix.cli import on_progress

def get_video_streams(url):
    try:
        yt = YouTube(url,on_progress_callback = on_progress)
        streams = yt.streams.filter(progressive=True).all()
        return streams
    except VideoUnavailable:
        print(f"Video {url} is unavailable.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def display_streams(streams):
    if streams:
        for i, stream in enumerate(streams):
            print(f"{i + 1}. {stream.resolution} - {stream.mime_type}")
    else:
        print("No streams available.")

def download_video(stream):
    if stream:
        stream.download()
        print("Download completed!")
    else:
        print("No stream selected for download.")

if __name__ == "__main__":
    video_url = input("Enter the YouTube video URL: ").split('&')[0]  # Remove any additional parameters
    streams = get_video_streams(video_url)
    display_streams(streams)
    
    if streams:
        choice = int(input("Select the quality option (number): ")) - 1
        selected_stream = streams[choice]
        download_video(selected_stream)
