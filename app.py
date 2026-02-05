import os
import ssl
from flask import Flask, request, jsonify
from flask_cors import CORS
from pytube import YouTube

# 修正 SSL 與年齡限制
ssl._create_default_https_context = ssl._create_stdlib_context
from pytube.innertube import _default_clients
_default_clients["ANDROID_MUSIC"] = _default_clients["ANDROID_CREATOR"]

app = Flask(__name__)
CORS(app)  # 這很重要，允許你的 GitHub 網頁連線到這個後端

@app.route('/download', methods=['POST'])
def download_video():
    data = request.json
    url = data.get('url')
    file_type = data.get('type')
    res = data.get('res')

    try:
        yt = YouTube(url)
        if file_type == 'MP4':
            # 尋找指定畫質，找不到則用最高畫質
            stream = yt.streams.filter(res=res, file_extension='mp4').first() or yt.streams.get_highest_resolution()
        else:
            stream = yt.streams.get_audio_only()
        
        # 下載到伺服器暫存區（Render 的硬碟空間有限）
        stream.download()
        return jsonify({"status": "success", "msg": f"已成功解析並開始下載：{yt.title}"})
    except Exception as e:
        return jsonify({"status": "error", "msg": str(e)})

if __name__ == '__main__':
    app.run()
