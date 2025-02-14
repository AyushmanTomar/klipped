from flask import Flask,request,render_template, send_file,url_for,redirect, after_this_request,jsonify
from moviepy.editor import *
from pytubefix import YouTube
from pytube.exceptions import VideoUnavailable
import re
import time
from flask_socketio import SocketIO, emit
from proglog import ProgressBarLogger
import os
from youtube_transcript_api import YouTubeTranscriptApi


def extract_video_id(url):
    pattern = r'(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})'
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    return None

def get_video_info(url):
    try:
        yt = YouTube(url,use_po_token=True)
    except VideoUnavailable:
        print(f"Video {url} is unavailable.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    return yt

def clearclip():
    dir = os.listdir('clip/')
    for file in dir:
        if dir != 'CLIP.txt':
            os.remove('clip/'+file)

    


app=Flask(__name__)

socketio = SocketIO(app)

class MyBarLogger(ProgressBarLogger):
    def callback(self, **changes):
        for (parameter, value) in changes.items():
            print('Parameter %s is now %s' % (parameter, value))

    def bars_callback(self, bar, attr, value, old_value=None):
        percentage = (value / self.bars[bar]['total']) * 100
        # print(bar, attr, percentage)
        socketio.emit('progress', {'progress': percentage})


@app.route('/')
def homepage():
    clearclip()
    error = request.args.get('error')
    return render_template('index.html',error = error)

@app.route('/download',methods=['POST'])
def download():
    url = request.form['url']
    id  = extract_video_id(url)
    if id == None:
        return  redirect(url_for('homepage',error='INVALID URL! ENTER AGAIN'))
    yt = get_video_info(url)
    if yt== None:
        return  redirect(url_for('homepage',error='Video not Available'))
    streams_prog = yt.streams.filter(progressive=True).all()
    streams_audio = yt.streams.filter(only_audio=True).all()
    streams_high = yt.streams.filter(res=['1080p','720p'],file_extension='mp4')

    return render_template('download.html',url=url,vidid=id,title=yt.title,streams_prog=streams_prog,streams_audio=streams_audio,streams_high=streams_high)

@app.route('/getvideo',methods=['POST'])
def getvideo():
    render_template('index.html')
    itag = request.form['itag']
    url = request.form['url']
    yt = get_video_info(url)
    v = yt.streams.get_by_itag(itag)
    
    if v.is_progressive or v.includes_audio_track:  
        filename = v.download("clip\\")
        return send_file(filename,as_attachment=True)
    else:
        vid_file = v.download(filename='video.mp4')
        audio_stream = yt.streams.filter(only_audio=True).first()
        audio_file = audio_stream.download(filename='audio.mp4')
        time.sleep(3)
        video_clip = VideoFileClip("video.mp4")
        audio_clip = AudioFileClip("audio.mp4")
        output_path = "clip\\"+yt.title+".mp4"
        video_clip_with_audio = video_clip.set_audio(audio_clip)
        progress_logger = MyBarLogger()
        video_clip_with_audio.write_videofile(output_path,codec='libx264',logger=progress_logger)
        @after_this_request
        def delete_file(response):
            try:
                os.remove('video.mp4')
                os.remove('audio.mp4')
                video_clip_with_audio.close()
                video_clip.close()
                audio_clip.close()
                # time.sleep(3)
                # os.remove(yt.title+".mp4")
                return response
            except Exception as error:
                app.logger.error("Error removing downloaded file", error)
                return response
        return send_file(output_path, as_attachment=True)
    

@app.route('/summarize')
def summaryy():
    return render_template('summary.html')

@app.route('/getsummary',methods=['POST'])
def getsummary():
    url = request.form['url']
    id  = extract_video_id(url)
    if id == None:
        return  jsonify({'error':"Enter Correct URL! "})
    yt = get_video_info(url)
    if yt== None:
        return  jsonify({'error':"Enter Correct URL! "})
    title=yt.title
    srt_list = YouTubeTranscriptApi.list_transcripts(id)
    print(srt_list)
    srt = srt_list.find_generated_transcript(['hi'])
    translated_srt=srt.translate('en')
    srt_file = translated_srt.fetch()
    print(srt_file)
    str=""
    for i in srt_file:
        str=str+" "+i['text']
    summary=str
    id = 'https://img.youtube.com/vi/'+id+'/hqdefault.jpg'
    return jsonify({'url':url,'summary':summary,'thumbnail':id,'title':title})
    
    


if __name__ == '__main__':
    app.run(debug=False)
