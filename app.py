import os
import subprocess
from flask import Flask, render_template, request
from pytube import YouTube
from googleapiclient.discovery import build
from urllib.parse import urlparse, parse_qs

app = Flask(__name__)
app.config['DEBUG'] = True
YOUTUBE_API_KEY = ''


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/search', methods=['POST'])
def search():
    query = request.form['query']
    search_results = perform_search(query)
    return render_template('search.html', results=search_results)

@app.route('/download', methods=['GET'])
def download():
    url = request.args.get('url')
    if not url.startswith('https://www.youtube.com/watch?v='):
        raise ValueError("Invalid YouTube URL")

    download_type = request.args.get('download_type')

    if download_type == 'video':
        return get_video_streams(url)
    elif download_type == 'mp3':
        download_mp3(url)
        return "Downloaded successfully!"


def perform_search(query):
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
    search_response = youtube.search().list(
        q=query,
        type='video',
        part='id,snippet',
        maxResults=10
    ).execute()

    results = []
    for search_result in search_response.get('items', []):
        video_id = search_result['id']['videoId']
        title = search_result['snippet']['title']
        results.append({'video_id': video_id, 'title': title})

    return results


def get_video_streams(url):
    parsed_url = urlparse(url)
    video_id = parse_qs(parsed_url.query).get('v')
    if video_id:
        video_id = video_id[0]
    else:
        raise ValueError("Invalid YouTube URL")

    yt = YouTube(f"https://www.youtube.com/watch?v={video_id}")
    video_streams = yt.streams.filter(file_extension='mp4', progressive=True).all()
    return render_template('download.html', url=url, streams=video_streams, download_type='video')


def download_mp3(url):
    # Code to download mp3
    pass


if __name__ == '__main__':
    app.run()
