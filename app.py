import os
import ssl
from flask import Flask, request, jsonify
from flask_cors import CORS
from pytube import YouTube
from pytube.exceptions import VideoUnavailable, AgeRestrictedError, PytubeError

# 修正 SSL 安全性問題
ssl._create_default_https_context = ssl._create_stdlib_context

# 強制修正 pytube 內部客戶端設定，模擬 Creator 模式避開 400 錯誤
from pytube.innertube import _default_clients
_default_clients["ANDROID_MUSIC"] = _default_clients["ANDROID_CREATOR"]
_default_clients["ANDROID"] = _default_clients["ANDROID_CREATOR"]
_default_clients["IOS"] = _default_clients["ANDROID_CREATOR"]

app = Flask(__name__)
CORS(app)  # 允許 GitHub Pages 的跨網域請求

@app.route('/')
def home():
    return "YouTube Downloader Backend is Running!"

@app.route('/download', methods=['POST'])
def download_video():
    data = request.json
    url = data.get('url')
    file_type = data.get('type')
    res = data.get('res')

    if not url:
        return jsonify({"status": "error", "msg": "未提供網址"}), 400

    try:
        # 初始化 YouTube 物件，加入建議參數
        yt = YouTube(
            url,
            use_oauth=False,
            allow_oauth_cache=True
        )

        if file_type == 'MP4':
            # 優先找使用者選的畫質
            stream = yt.streams.filter(res=res, file_extension='mp4', progressive=True).first()
            # 如果找不到或是該畫質不支援(例如沒聲音的分離檔)，改抓最高畫質
            if not stream:
                stream = yt.streams.get_highest_resolution()
        else:
            # 下載音訊
            stream = yt.streams.get_audio_only()

        if not stream:
            return jsonify({"status": "error", "msg": "找不到適合的串流"}), 404

        # 下載至伺服器暫存資料夾
        filename = f"download_{yt.video_id}.{file_type.lower()}"
        stream.download(output_path="/tmp", filename=filename)

        return jsonify({
            "status": "success", 
            "msg": f"解析成功！影片標題：{yt.title}。檔案已準備好在伺服器端（註：免費版伺服器空間有限，檔案不會永久儲存）。"
        })

    except AgeRestrictedError:
        return jsonify({"status": "error", "msg": "此影片受年齡限制，無法在伺服器端下載。"}), 403
    except VideoUnavailable:
        return jsonify({"status": "error", "msg": "影片無法使用（可能已刪除或私有）。"}), 404
    except Exception as e:
        print(f"後端報錯: {str(e)}") # 方便在 Render Logs 查看
        return jsonify({"status": "error", "msg": f"下載發生錯誤: {str(e)}"}), 500

if __name__ == '__main__':
    # Render 會自動偵測 PORT
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
