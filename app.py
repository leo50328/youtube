import os
import ssl
from flask import Flask, request, jsonify
from flask_cors import CORS
from pytube import YouTube
from pytube.exceptions import VideoUnavailable, AgeRestrictedError

# SSL 修正
ssl._create_default_https_context = ssl._create_stdlib_context

# --- 防封鎖核心修正 ---
from pytube.innertube import _default_clients
# 強制所有請求使用 Web 客戶端模擬，這能避開多數 400 錯誤
_default_clients["ANDROID"] = _default_clients["WEB"]
_default_clients["ANDROID_MUSIC"] = _default_clients["WEB"]
_default_clients["IOS"] = _default_clients["WEB"]

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return "Backend Active"

@app.route('/download', methods=['POST'])
def download_video():
    data = request.json
    url = data.get('url')
    file_type = data.get('type')
    res = data.get('res')

    try:
        # 加入更多參數，模擬真實行為
        yt = YouTube(url, use_oauth=False, allow_oauth_cache=True)
        
        if file_type == 'MP4':
            # progressive=True 確保抓到有聲音又有影像的單一檔案
            stream = yt.streams.filter(res=res, file_extension='mp4', progressive=True).first()
            if not stream:
                stream = yt.streams.get_highest_resolution()
        else:
            stream = yt.streams.get_audio_only()

        if not stream:
            return jsonify({"status": "error", "msg": "找不到合適的串流"})

        # 下載至 /tmp 暫存區
        stream.download(output_path="/tmp")
        
        return jsonify({
            "status": "success", 
            "msg": f"解析成功！已在後端完成處理：{yt.title}"
        })

    except Exception as e:
        print(f"Error details: {str(e)}") # 這會出現在 Render Logs
        return jsonify({"status": "error", "msg": f"下載發生錯誤: {str(e)}"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
