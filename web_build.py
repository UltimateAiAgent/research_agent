# run_with_ngrok.py
import os, subprocess, sys, time, webbrowser
from threading import Thread
from pyngrok import ngrok
from dotenv import load_dotenv

# ---------------- 設定 ---------------- #
LOCAL_PORT = 8501          # Streamlit 預設
STREAMLIT_FILE = "app.py"  # 你的主程式

# 讀 .env
load_dotenv(override=True)

# 檢查 ngrok token ── 建議放在 .env： NGROK_AUTH_TOKEN=<your token>
token = os.getenv("NGROK_AUTH_TOKEN")
if not token:
    print("❌  找不到 NGROK_AUTH_TOKEN！先去 https://dashboard.ngrok.com/ 申請，再放到 .env")
    sys.exit(1)

ngrok.set_auth_token(token)

# ---------------- 開 streamlit ---------------- #
def run_streamlit():
    # 以子行程執行，stderr/stdout 重導向到目前終端
    cmd = ["streamlit", "run", STREAMLIT_FILE, "--server.port", str(LOCAL_PORT)]
    subprocess.run(cmd)

Thread(target=run_streamlit, daemon=True).start()

# Streamlit 啟動要幾秒；你也可以直接 sleep(5) 粗暴等待
print("⏳ 等待 Streamlit 啟動 ...")
while True:
    # 簡單檢查埠口是否打開
    import socket
    s = socket.socket()
    try:
        s.connect(("localhost", LOCAL_PORT))
        s.close()
        break
    except socket.error:
        time.sleep(1)

# ---------------- 開 ngrok ---------------- #
public_tunnel = ngrok.connect(addr=LOCAL_PORT, proto="http")
public_url = public_tunnel.public_url
print(f"🚀  Public URL: {public_url}")

# 自動打開瀏覽器（可省略）
webbrowser.open(public_url)

# 主執行緒維持；CTRL-C 結束
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n🛑  Shutting down ...")
    ngrok.disconnect(public_url)
    ngrok.kill()