from flask import Flask, request, jsonify, send_file
import youtube_dl
from youtube_search import YoutubeSearch
import requests
import os
from config import Config

app = Flask(__name__)

# Convert hh:mm:ss to seconds
def time_to_seconds(time):
    stringt = str(time)
    return sum(int(x) * 60 ** i for i, x in enumerate(reversed(stringt.split(':'))))

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    if not query:
        return jsonify({'error': 'No query provided'}), 400

    ydl_opts = {"format": "bestaudio[ext=m4a]"}
    try:
        results = []
        count = 0
        while len(results) == 0 and count < 6:
            if count > 0:
                time.sleep(1)
            results = YoutubeSearch(query, max_results=1).to_dict()
            count += 1

        if not results:
            return jsonify({'error': 'No results found'}), 404

        result = results[0]
        link = f"https://youtube.com{result['url_suffix']}"
        title = result["title"]
        thumbnail = result["thumbnails"][0]
        duration = result["duration"]
        views = result["views"]
        thumb_name = f'thumb{title}.jpg'
        thumb = requests.get(thumbnail, allow_redirects=True)
        with open(thumb_name, 'wb') as thumb_file:
            thumb_file.write(thumb.content)

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(link, download=False)
            audio_file = ydl.prepare_filename(info_dict)
            ydl.process_info(info_dict)

        response = {
            'title': title,
            'duration': duration,
            'views': views,
            'link': link,
            'audio_file': audio_file,
            'thumbnail': thumb_name
        }
        return jsonify(response)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download', methods=['GET'])
def download():
    file_path = request.args.get('file_path')
    if not file_path or not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404

    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
        
