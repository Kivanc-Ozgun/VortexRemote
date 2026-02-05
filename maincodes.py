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
import os
import random
import string
from PIL import Image
from urllib.parse import urlparse, parse_qs

pyautogui.PAUSE = 0
pyautogui.FAILSAFE = False

# Generate a unique session key
SESSION_KEY = ''.join(random.choices(string.ascii_letters + string.digits, k=6))

def add_firewall_rule():
    rule_name = "Vortex Remote Allow"
    port = 5555
    cmd = f'netsh advfirewall firewall add rule name="{rule_name}" dir=in action=allow protocol=TCP localport={port} profile=any'
    try:
        subprocess.run(cmd, shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except:
        pass

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

class VortexRemoteHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args): return

    def do_GET(self):
        query = parse_qs(urlparse(self.path).query)
        received_key = query.get('key', [None])[0]

        if self.path.startswith('/api'):
            if received_key != SESSION_KEY:
                self.send_response(403)
                self.end_headers()
                return
            
            try:
                cmd = query.get('cmd', [None])[0]
                if cmd == 'move':
                    pyautogui.moveRel(float(query.get('dx', [0])[0]) * 2.5, float(query.get('dy', [0])[0]) * 2.5)
                elif cmd == 'scroll':
                    pyautogui.scroll(int(float(query.get('dy', [0])[0]) * -35))
                elif cmd == 'click': pyautogui.click()
                elif cmd == 'rclick': pyautogui.rightClick()
                elif cmd == 'type': pyautogui.write(query.get('text', [""])[0])
                elif cmd == 'key': pyautogui.press(query.get('key', [""])[0])
            except: pass
            
            self.send_response(200)
            self.end_headers()
            return

        if self.path.startswith('/?key=' + SESSION_KEY) or received_key == SESSION_KEY:
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            html = f"""
            <!DOCTYPE html><html><head>
            <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
            <style>
                body{{margin:0;background:#0f172a;color:white;font-family:sans-serif;overflow:hidden;touch-action:none;user-select:none;}}
                .main{{display:flex;flex-direction:column;height:100vh;height:100dvh;padding:10px;box-sizing:border-box;}}
                .header{{text-align:center;margin-bottom:5px;}}
                .header h3{{color:#3b82f6;margin:0;font-size:18px;}}
                .top-bar{{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-bottom:10px;}}
                .btn-s{{background:#334155;padding:12px 2px;border-radius:8px;text-align:center;font-size:11px;font-weight:bold;border:1px solid #475569;}}
                .kb-area{{display:flex;gap:8px;margin-bottom:10px;}}
                input{{flex-grow:1;padding:10px;border-radius:10px;border:1px solid #334155;background:#1e293b;color:white;font-size:16px;outline:none;}}
                .send-btn{{background:#2563eb;padding:10px 15px;border-radius:10px;font-weight:bold;font-size:13px;}}
                .center-area{{display:flex;flex:1;min-height:100px;gap:10px;margin-bottom:10px;overflow:hidden;}}
                #tp{{flex:1;background:#1e293b;border-radius:20px;border:2px solid #3b82f6;display:flex;align-items:center;justify-content:center;color:#3b82f6;font-weight:bold;}}
                #sp{{width:60px;background:#1e293b;border-radius:20px;border:2px solid #64748b;display:flex;align-items:center;justify-content:center;writing-mode:vertical-rl;color:#64748b;font-weight:bold;}}
                .mouse-btns{{display:grid;grid-template-columns:1fr 1fr;gap:10px;height:75px;margin-bottom:5px;}}
                .big-btn{{background:#334155;border-radius:15px;display:flex;align-items:center;justify-content:center;font-size:16px;font-weight:bold;border-bottom:4px solid #0f172a;}}
                .big-btn:active{{background:#3b82f6;border-bottom:0;transform:translateY(2px);}}
            </style></head><body><div class="main">
                <div class="header"><h3>🌀 VORTEX REMOTE</h3><span style="font-size:10px;opacity:0.5;">Created by Kivanc</span></div>
                <div class="top-bar">
                    <div class="btn-s" onclick="a('cmd=key&key=esc')">ESC</div>
                    <div class="btn-s" onclick="a('cmd=key&key=backspace')">BACK</div>
                    <div class="btn-s" onclick="a('cmd=key&key=enter')">ENTER</div>
                    <div class="btn-s" onclick="a('cmd=key&key=space')">SPACE</div>
                </div>
                <div class="kb-area"><input type="text" id="it" placeholder="Type here..."><div class="send-btn" onclick="st()">SEND</div></div>
                <div class="center-area"><div id="tp">TOUCHPAD</div><div id="sp">SCROLL</div></div>
                <div class="mouse-btns"><div class="big-btn" onclick="a('cmd=click')">LEFT CLICK</div><div class="big-btn" onclick="a('cmd=rclick')">RIGHT CLICK</div></div>
            </div><script>
                let lx=0,ly=0,sl=0;const tp=document.getElementById('tp'),sp=document.getElementById('sp');
                tp.addEventListener('touchstart',e=>{{lx=e.touches[0].clientX;ly=e.touches[0].clientY;}});
                tp.addEventListener('touchmove',e=>{{const dx=(e.touches[0].clientX-lx)*1.3,dy=(e.touches[0].clientY-ly)*1.3;lx=e.touches[0].clientX;ly=e.touches[0].clientY;a(`cmd=move&dx=${{dx}}&dy=${{dy}}`);}});
                sp.addEventListener('touchstart',e=>{{sl=e.touches[0].clientY;}});
                sp.addEventListener('touchmove',e=>{{const dy=e.touches[0].clientY-sl;sl=e.touches[0].clientY;a(`cmd=scroll&dy=${{dy}}`);}});
                function a(p){{fetch('/api?key={SESSION_KEY}&'+p).catch(e=>{{}});}}
                function st(){{const i=document.getElementById('it');a('cmd=type&text='+encodeURIComponent(i.value));i.value='';}}
            </script></body></html>
            """
            self.wfile.write(html.encode('utf-8'))
        else:
            self.send_response(403)
            self.end_headers()
            self.wfile.write(b"403 Forbidden: Access Denied")

class VortexRemote(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("VORTEX REMOTE")
        self.geometry("500x700")
        self.server = None
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
        
        self.dev_label = ctk.CTkLabel(self, text="Professional Security Enabled", font=("Arial", 12, "italic"), text_color="#64748b")
        self.dev_label.pack(pady=(0, 20))
        
        self.btn = ctk.CTkButton(self, text="START REMOTE SERVER", font=("Arial", 14, "bold"), height=50, fg_color="#2563eb", command=self.start)
        self.btn.pack(pady=10)

        self.fix_btn = ctk.CTkButton(self, text="FIX FIREWALL", font=("Arial", 12), height=30, fg_color="#f59e0b", command=self.fix_conn)
        self.fix_btn.pack(pady=5)
        
        self.qr_label = ctk.CTkLabel(self, text="")
        self.qr_label.pack(pady=20)
        
        self.status = ctk.CTkLabel(self, text=f"Auth Key: {SESSION_KEY}", text_color="#3b82f6", font=("Consolas", 14))
        self.status.pack(side="bottom", pady=20)

    def fix_conn(self):
        if is_admin():
            add_firewall_rule()
            self.fix_btn.pack_forget()
        else:
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
            sys.exit()

    def start(self):
        if is_admin(): add_firewall_rule(); self.fix_btn.pack_forget()
        ip = self.get_ip()
        port = 5555
        url = f"http://{ip}:{port}/?key={SESSION_KEY}"
        
        qr = qrcode.make(url)
        buf = io.BytesIO(); qr.save(buf, format="PNG"); buf.seek(0)
        img = ctk.CTkImage(Image.open(buf), size=(250, 250))
        
        self.qr_label.configure(image=img)
        self.btn.configure(state="disabled", text="SERVER ONLINE")
        
        def run():
            with socketserver.ThreadingTCPServer(("0.0.0.0", port), VortexRemoteHandler) as httpd:
                httpd.allow_reuse_address = True
                httpd.serve_forever()
        threading.Thread(target=run, daemon=True).start()

if __name__ == "__main__":
    app = VortexRemote()
    app.mainloop()
