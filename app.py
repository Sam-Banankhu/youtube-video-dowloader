from flask import Flask, render_template, request
from pytube import YouTube
import youtube_dl
from pydub import AudioSegment

app = Flask(__name__)
app.config['DEBUG'] = True


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    url = request.form['url']
    download_type = request.form['download_type']

    if download_type == 'video':
        download_video(url)
    elif download_type == 'mp3':
        download_mp3(url)

    return "Downloaded successfully!"

def download_video(url):
    yt = YouTube(url)
    yt.streams.get_highest_resolution().download()

def download_mp3(url):
    yt = YouTube(url)
    audio_stream = yt.streams.filter(only_audio=True, mime_type='audio/webm').first()
    output_path = '/home/pandas/Desktop/projects/tubedl'  
    audio_stream.download(output_path)

    # Convert the downloaded .webm file to .mp3 using pydub
    webm_filename = f"{yt.title}.webm"
    mp3_filename = f"{yt.title}.mp3"
    webm_filepath = f"{output_path}/{webm_filename}"
    mp3_filepath = f"{output_path}/{mp3_filename}"

    # Use pydub to load the .webm file and save it as .mp3
    audio = AudioSegment.from_file(webm_filepath, format="webm")
    audio.export(mp3_filepath, format="mp3")


if __name__ == '__main__':
    app.run()
