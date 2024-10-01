from flask import Flask, render_template, request, redirect, url_for, send_file
import requests
from typing import List, Dict

app = Flask(__name__)

YANDEX_API_URL = "https://cloud-api.yandex.net/v1/disk/public/resources"


def get_public_files(public_key: str) -> List[Dict]:
    """Получаем список файлов и папок по публичной ссылке (public_key)."""
    params = {'public_key': public_key}
    response = requests.get(YANDEX_API_URL, params=params)
    if response.status_code == 200:
        items = response.json()['_embedded']['items']
        return items
    return []


@app.route('/', methods=['GET', 'POST'])
def index():
    files = []
    if request.method == 'POST':
        public_key = request.form.get('public_key')
        if public_key:
            files = get_public_files(public_key)
    return render_template('index.html', files=files)


@app.route('/download', methods=['POST'])
def download_file():
    file_url = request.form.get('file_url')
    file_name = request.form.get('file_name')

    if file_url and file_name:
        response = requests.get(file_url, stream=True)
        file_path = f"./{file_name}"

        with open(file_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)

        return send_file(file_path, as_attachment=True)

    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
