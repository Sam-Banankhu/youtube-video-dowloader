import os
import subprocess
from flask import Flask, render_template, request
from pytube import YouTube

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
        available_streams = get_video_streams(url)
    elif download_type == 'mp3':
        available_streams = get_audio_streams(url)

    return render_template('download.html', url=url, download_type=download_type, streams=available_streams)


@app.route('/download_media', methods=['POST'])
def download_media():
    url = request.form['url']
    download_type = request.form['download_type']
    selected_stream = request.form['selected_stream']

    if download_type == 'video':
        downloaded_file = download_video(url, selected_stream)
        if downloaded_file:
            open_folder(os.path.dirname(downloaded_file))
    elif download_type == 'mp3':
        downloaded_file = download_mp3(url, selected_stream)
        if downloaded_file:
            open_folder(os.path.dirname(downloaded_file))

    return "Downloaded successfully!"


def get_video_streams(url):
    yt = YouTube(url)
    return yt.streams.filter(file_extension='mp4')


def get_audio_streams(url):
    yt = YouTube(url)
    return yt.streams.filter(only_audio=True, file_extension='webm')


def download_video(url, itag):
    yt = YouTube(url)
    output_path = os.path.expanduser('~/Videos')  # Use system default video folder
    video_stream = yt.streams.get_by_itag(itag)
    if video_stream:
        video_file = video_stream.download(output_path)
        return video_file
    return None


def download_mp3(url, itag):
    yt = YouTube(url)
    audio_stream = yt.streams.get_by_itag(itag)
    if audio_stream:
        output_path = os.path.expanduser('~/Music')  # Use system default music folder
        audio_file = audio_stream.download(output_path)

        # Convert the downloaded .webm audio to .mp3 using ffmpeg
        webm_filename = f"{yt.title}.webm"
        mp3_filename = f"{yt.title}.mp3"
        webm_filepath = os.path.join(output_path, webm_filename)
        mp3_filepath = os.path.join(output_path, mp3_filename)

        # Use subprocess to call ffmpeg and convert the .webm file to .mp3
        subprocess.run(['ffmpeg', '-i', webm_filepath, mp3_filepath])

        # Remove the original .webm file
        os.remove(webm_filepath)

        return mp3_filepath
    return None


def open_folder(folder_path):
    if os.name == 'nt':  # Windows
        subprocess.run(['explorer', folder_path])
    elif os.name == 'posix':  # Linux and macOS
        subprocess.run(['xdg-open', folder_path])


if __name__ == '__main__':
    app.run()
