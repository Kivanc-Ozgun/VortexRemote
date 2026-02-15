import customtkinter as ctk
import qrcode
import socket
import http.server
import socketserver
import threading
import io
import pyautogui
import sys
import ctypes
import subprocess
import random
import string
import pyperclip  # Türkçe karakterler için gerekli
from PIL import Image, ImageGrab, ImageDraw
from urllib.parse import urlparse, parse_qs

# Ayarlar
pyautogui.PAUSE = 0
pyautogui.FAILSAFE = False
SESSION_KEY = ''.join(random.choices(string.ascii_letters + string.digits, k=6))

def add_firewall_rule():
    try:
        rule_name = "Vortex Remote Allow"
        port = 5555
        cmd = f'netsh advfirewall firewall add rule name="{rule_name}" dir=in action=allow protocol=TCP localport={port} profile=any'
        subprocess.run(cmd, shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except: pass

class VortexRemoteHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args): return

    def do_GET(self):
        query = parse_qs(urlparse(self.path).query)
        received_key = query.get('key', [None])[0]

        # 1. API KOMUTLARI
        if self.path.startswith('/api'):
            if received_key != SESSION_KEY: return
            try:
                cmd = query.get('cmd', [None])[0]
                if cmd == 'move':
                    pyautogui.moveRel(float(query.get('dx', [0])[0]) * 2.2, float(query.get('dy', [0])[0]) * 2.2)
                elif cmd == 'scroll':
                    pyautogui.scroll(int(float(query.get('dy', [0])[0]) * -35))
                elif cmd == 'click': pyautogui.click()
                elif cmd == 'rclick': pyautogui.rightClick()
                elif cmd == 'type':
                    # TÜRKÇE KARAKTER ÇÖZÜMÜ: Panoya kopyala ve yapıştır
                    text = query.get('text', [""])[0]
                    pyperclip.copy(text)
                    pyautogui.hotkey('ctrl', 'v')
                elif cmd == 'key': pyautogui.press(query.get('key', [""])[0])
            except: pass
            self.send_response(200); self.end_headers(); return

        # 2. EKRAN YAYINI (HD)
        if self.path.startswith('/screen'):
            if received_key != SESSION_KEY: return
            img = ImageGrab.grab()
            draw = ImageDraw.Draw(img)
            mx, my = pyautogui.position()
            r = 12
            draw.ellipse((mx-r, my-r, mx+r, my+r), fill="#3b82f6", outline="white", width=3)
            
            # Netlik için 960x540 ve Bilinear filtre
            img = img.resize((960, 540), Image.Resampling.BILINEAR)
            buffer = io.BytesIO()
            img.save(buffer, format="JPEG", quality=75, optimize=True)
            
            self.send_response(200)
            self.send_header('Content-type', 'image/jpeg')
            self.end_headers()
            self.wfile.write(buffer.getvalue())
            return

        # 3. ARAYÜZ (HTML/CSS)
        if self.path.startswith('/?key=' + SESSION_KEY) or received_key == SESSION_KEY:
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            html = f"""
            <!DOCTYPE html><html><head>
            <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
            <style>
                body{{margin:0;background:#0f172a;color:white;font-family:sans-serif;overflow:hidden;touch-action:none;user-select:none;}}
                .main{{display:flex;flex-direction:column;height:100dvh;padding:10px;box-sizing:border-box;}}
                .header{{text-align:center;margin-bottom:8px;}}
                .header h3{{color:#3b82f6;margin:0;font-size:18px;}}
                .screen-container{{width:100%;background:#000;border-radius:12px;overflow:hidden;margin-bottom:10px;border:2px solid #1e293b;line-height:0;}}
                #screen-img{{width:100%;height:auto;display:block;}}
                .top-bar{{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-bottom:10px;}}
                .btn-s{{background:#334155;padding:12px 2px;border-radius:8px;text-align:center;font-size:11px;font-weight:bold;border:1px solid #475569;}}
                .kb-area{{display:flex;gap:8px;margin-bottom:10px;}}
                input{{flex-grow:1;padding:10px;border-radius:10px;border:1px solid #334155;background:#1e293b;color:white;font-size:16px;outline:none;}}
                .send-btn{{background:#2563eb;padding:10px 15px;border-radius:10px;font-weight:bold;font-size:13px;display:flex;align-items:center;}}
                .center-area{{display:flex;flex:1;min-height:100px;gap:10px;margin-bottom:10px;}}
                #tp{{flex:1;background:#1e293b;border-radius:20px;border:2px solid #3b82f6;display:flex;align-items:center;justify-content:center;color:#3b82f6;font-weight:bold;}}
                #sp{{width:60px;background:#1e293b;border-radius:20px;border:2px solid #64748b;display:flex;align-items:center;justify-content:center;writing-mode:vertical-rl;color:#64748b;font-weight:bold;}}
                .mouse-btns{{display:grid;grid-template-columns:1fr 1fr;gap:10px;height:75px;}}
                .big-btn{{background:#334155;border-radius:15px;display:flex;align-items:center;justify-content:center;font-size:16px;font-weight:bold;border-bottom:4px solid #000;}}
                .big-btn:active{{background:#3b82f6;border-bottom:0;transform:translateY(2px);}}
            </style></head><body><div class="main">
                <div class="header"><h3>🌀 VORTEX REMOTE HD</h3></div>
                <div class="screen-container"><img id="screen-img" src=""></div>
                <div class="top-bar">
                    <div class="btn-s" onclick="a('cmd=key&key=esc')">ESC</div>
                    <div class="btn-s" onclick="a('cmd=key&key=backspace')">BACK</div>
                    <div class="btn-s" onclick="a('cmd=key&key=enter')">ENTER</div>
                    <div class="btn-s" onclick="a('cmd=key&key=space')">SPACE</div>
                </div>
                <div class="kb-area"><input type="text" id="it" placeholder="Yazın..."><div class="send-btn" onclick="st()">GÖNDER</div></div>
                <div class="center-area"><div id="tp">TOUCHPAD</div><div id="sp">SCROLL</div></div>
                <div class="mouse-btns"><div class="big-btn" onclick="a('cmd=click')">SOL TIK</div><div class="big-btn" onclick="a('cmd=rclick')">SAĞ TIK</div></div>
            </div><script>
                const key = "{SESSION_KEY}";
                const screenImg = document.getElementById('screen-img');
                function updateScreen() {{ screenImg.src = "/screen?key=" + key + "&t=" + Date.now(); }}
                screenImg.onload = () => {{ setTimeout(updateScreen, 40); }};
                updateScreen();
                let lx=0,ly=0,sl=0;
                const tp=document.getElementById('tp'), sp=document.getElementById('sp');
                tp.addEventListener('touchstart',e=>{{lx=e.touches[0].clientX;ly=e.touches[0].clientY;e.preventDefault();}},{{passive:false}});
                tp.addEventListener('touchmove',e=>{{
                    const dx=(e.touches[0].clientX-lx); const dy=(e.touches[0].clientY-ly);
                    lx=e.touches[0].clientX; ly=e.touches[0].clientY;
                    a(`cmd=move&dx=${{dx}}&dy=${{dy}}`); e.preventDefault();
                }},{{passive:false}});
                sp.addEventListener('touchstart',e=>{{sl=e.touches[0].clientY; e.preventDefault();}},{{passive:false}});
                sp.addEventListener('touchmove',e=>{{
                    const dy=e.touches[0].clientY-sl; sl=e.touches[0].clientY;
                    a(`cmd=scroll&dy=${{dy}}`); e.preventDefault();
                }},{{passive:false}});
                function a(p){{fetch('/api?key='+key+'&'+p).catch(e=>{{}});}}
                function st(){{const i=document.getElementById('it'); if(i.value){{ a('cmd=type&text='+encodeURIComponent(i.value)); i.value=''; }}}}
            </script></body></html>
            """
            self.wfile.write(html.encode('utf-8'))
        else:
            self.send_response(403); self.end_headers()

class VortexRemote(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("VORTEX REMOTE PRO")
        self.geometry("450x650")
        self.setup_ui()

    def get_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except: return "127.0.0.1"

    def setup_ui(self):
        ctk.set_appearance_mode("Dark")
        self.label = ctk.CTkLabel(self, text="VORTEX REMOTE", font=("Arial", 32, "bold"), text_color="#3b82f6")
        self.label.pack(pady=(30, 5))
        self.btn = ctk.CTkButton(self, text="START SERVER", font=("Arial", 14, "bold"), height=50, command=self.start)
        self.btn.pack(pady=10)
        self.qr_label = ctk.CTkLabel(self, text="")
        self.qr_label.pack(pady=20)
        self.status = ctk.CTkLabel(self, text=f"Auth Key: {SESSION_KEY}", text_color="#3b82f6", font=("Consolas", 14))
        self.status.pack(side="bottom", pady=20)

    def start(self):
        add_firewall_rule()
        ip = self.get_ip()
        port = 5555
        url = f"http://{ip}:{port}/?key={SESSION_KEY}"
        qr = qrcode.make(url)
        buf = io.BytesIO(); qr.save(buf, format="PNG"); buf.seek(0)
        self.qr_label.configure(image=ctk.CTkImage(Image.open(buf), size=(250, 250)))
        self.btn.configure(state="disabled", text="SERVER ONLINE")
        threading.Thread(target=lambda: socketserver.ThreadingTCPServer(("0.0.0.0", port), VortexRemoteHandler).serve_forever(), daemon=True).start()

if __name__ == "__main__":
    VortexRemote().mainloop()
